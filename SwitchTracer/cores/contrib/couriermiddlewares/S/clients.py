import os
import pickle
import re
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from SwitchTracer.cores.contrib.couriermiddlewares import status
from SwitchTracer.cores.contrib.couriermiddlewares.componets.confs import vacancy_uniconf
from SwitchTracer.cores.contrib.couriermiddlewares.utills import MESSAGE_QUEUE, TASK_QUEUE, bytes_unit_switch
from SwitchTracer.universal.tools.functions import base64_switcher
from SwitchTracer.universal.exceptions import NoLocationErrors, ConfigureSyntaxErrors, \
    IllegalParametersErrors, UniErrors

BLOCKS = []
T = 0
# TODO: REPLACED BY VOLUME.GDICT
GDICT = {"checked": status.PREPARED}


class CourierManagerBase(object):

    __vacancy_conf__ = vacancy_uniconf
    __conf_prefix__ = ".download_%s.conf"
    __conf_pattern__ = re.compile(r"^(?P<key>[0-9A-Z_]+) = (?P<val>.*)$")
    __temp_prefix__ = "download_%s.temp"
    __cache_prefix__ = "download_%s.cache"

    def __init__(self, name: str, download_path: str = None):
        if not name:
            raise
        self.name = name
        self.download_path = download_path or os.path.dirname(__file__)
        self.conf = self.__vacancy_conf__
        self.seeds = []

    def resolute_settings_from_conf(self):
        conf = self.__conf_prefix__ % self.name
        location = os.path.join(self.download_path, conf)
        if not os.path.exists(location):
            raise NoLocationErrors("No configure<%s> has been found in path<%s>" % (conf, self.download_path))
        with open(location, "r") as f:
            for idx, line in enumerate(f.readlines()):
                if not line or line.startswith("#"):
                    continue
                ret = re.match(self.__conf_pattern__, line)
                if ret is None:
                    raise ConfigureSyntaxErrors(
                        "Syntax errors in conf<%s>'s Line %d, formats must be like 'KEY = value'" % (conf, idx)
                    )
                key, val = ret.groups()
                try:
                    setattr(self.conf, key.lower(), eval(val))
                except Exception as e:
                    raise ConfigureSyntaxErrors(
                        "Syntax errors in conf<%s>'s Line %d:\n\t %s" % (conf, idx, e)
                    )

    def index_seeds(self):
        # indexing from master Redis
        self.seeds = []
        MESSAGE_QUEUE.queue("! Indexing Seed from Redis")

    def check_md5(self, context: bytes, md5: str) -> int:
        return status.SUCCEEDED if hashlib.md5(context).hexdigest() == md5 else status.DESTROYED


class GenericCourierManager(CourierManagerBase):

    downloader_class = None
    cache_class = None
    abstract_master = None
    pool_exception_callback = None
    NULL = b'\x00'

    __remove__ = ["cache", "conf"]
    __parsers__ = {
        "base64": base64_switcher
    }

    __verbose__ = {
        status.SUCCEEDED: "\033[0;41m \033[0m",
        status.PREPARED: "\033[0;45m \033[0m",
        status.INFO: '\033[0;33m %s',
    }

    def __init__(self, name: str, download_path: str = None):
        super(GenericCourierManager, self).__init__(name, download_path)
        self.download_memory = None
        self.master = None

    def get_downloader_class(self):
        return self.downloader_class

    def get_downloader(self, server):
        return self.downloader_class(server)

    def get_cache_class(self):
        return self.cache_class

    def get_abstract_master(self):
        return self.abstract_master

    def get_callback(self):
        return self.pool_exception_callback()

    def download_initiation(self, mod=None, encoding=None):

        def writer(file, func):
            location = os.path.join(self.download_path, file)
            if os.path.exists(location):
                # TODO: LOG WARNING
                print("Overwrite warning: file<%s> has been existed in path<%s>" % (file, self.download_path))
            with open(location, "wb", encoding=encoding) as temp:
                func(temp)

        if mod == "T" or mod == "A":
            vacancy_memory = self.NULL * self.conf.memory
            writer(self.__temp_prefix__ % self.name, lambda f: f.write(vacancy_memory))
        if mod == "C" or mod == "A":
            blk_bit_flag = [status.PREPARED for _ in range(self.conf.total_blocks)]
            writer(self.__cache_prefix__ % self.name, lambda f: pickle.dump(blk_bit_flag, f))

        self.download_memory = self.get_cache_class()(
            os.path.join(self.download_path, self.__cache_prefix__ % self.name)
        )

    def loading_blocks(self):
        global BLOCKS, T
        # get download memory cache
        blocks_flags_bits = self.download_memory.cache
        BLOCKS = [str(i) for i, s in enumerate(blocks_flags_bits) if s == status.PREPARED]
        T = time.time()

    def request(self, block: int):
        # nonlocal master downloader shared among all threads
        status_, msg = self.master.connect(block)
        if status_ == status.SUCCEEDED:
            return status_, msg
        # seed urls from redis ordered by connect times.
        for seed in self.seeds:
            status_, msg = seed.connect(block)
            if status_ == status.SUCCEEDED:
                return status_, msg
        return status.PREPARED, "Sever Busy Now"

    def run(self, block: str):
        retries = self.conf.max_retries
        while retries:
            flag, msg = self.request(int(block))
            if flag == status.SUCCEEDED:
                msg = "$ %s at %.6f seconds" % (msg, time.time() - T)
                MESSAGE_QUEUE.queue(msg)
                return status.SUCCEEDED, block
            retries -= 1
            MESSAGE_QUEUE.queue(
                "# %s, block<%s> retry in %.2f seconds within %d times" % (msg, block, self.conf.timeout, retries)
            )
            time.sleep(self.conf.timeout)
        return status.TIMEOUT, block

    def write(self, verbose):
        with open(
                os.path.join(self.download_path, self.__temp_prefix__ % self.name), "rb+"
        ) as f:
            print("File<%s> starts at %s" % (self.conf.filename, time.ctime()))
            self._write(buffer=f, verbose=verbose)

    def task_parser(self, block: int, data: dict) -> (int, bytes, str):
        try:
            coder = self.__parsers__[data["encoding"]]
            content, md5 = coder("decode")(data["content"]), data["md5"]
        except KeyError as e:
            raise IllegalParametersErrors("Parameters: %s" % e)
        return block, content, md5

    def _write(self, buffer, verbose: bool):
        start = time.time()
        _start_ = start
        checked = self.conf.total_blocks - sum(self.download_memory.cache)
        seeds = []
        while checked < self.conf.total_blocks:
            task = TASK_QUEUE.dequeue()
            if task is None:
                time.sleep(0.5)
                continue
            block, context, md5 = self.task_parser(*task)
            status_ = self.check_md5(context, md5)
            if status_ > status.SUCCEEDED:
                BLOCKS.append(str(block))
                MESSAGE_QUEUE.queue("? Check ErrorCode(%d): block<%s>" % (status_, block))
                continue
            # write down
            self.write2file(block, context, buffer, verbose=verbose, startime=start)
            MESSAGE_QUEUE.queue("+ Write blocks<%s> Succeeded" % block)
            seeds.append(str(block))
            if len(seeds) and (
                    len(seeds) > self.conf.upload_frequency[0] or time.time() - _start_ > self.conf.upload_frequency[1]
            ):
                self.master.update_seeds(*seeds)
                MESSAGE_QUEUE.queue("! Upload seeds blocks[%s]" % ",".join(seeds))
                seeds = []
                _start_ = time.time()
            checked += 1
        GDICT["checked"] = status.SUCCEEDED

    def write2file(self, idx: int, context: bytes, buffer, verbose=True, startime=None):
        # write receive context to buffer
        buffer.seek(idx * self.conf.storage_per_blocks, 0)
        buffer.write(context)
        buffer.flush()
        # get download memory cache
        blocks_flags_bits = self.download_memory.cache
        # turn the written block to succeeded status
        blocks_flags_bits[idx] = status.SUCCEEDED
        # show verbose description
        if verbose:
            bar = "".join([self.__verbose__.get(i) for i in blocks_flags_bits])
            percent = (1 - sum(blocks_flags_bits) / self.conf.total_blocks) * 100
            times = ""
            if startime is not None:
                speed = (self.conf.total_blocks - sum(blocks_flags_bits)) / (time.time() - startime)
                last = round(sum(blocks_flags_bits) / speed, 2)
                speed, unit = bytes_unit_switch(speed * self.conf.storage_per_blocks)
                times = "-avg.speed: {s} {u}Bytes/s -approximate.last: {l} s".format(
                    s=round(speed, 2), u=unit, l=last
                )
            msg = "\r[%.2f %% %s] %s" % (percent, times, bar)
            print(self.__verbose__.get(status.INFO, ""), msg, end="")
        # overwrite download memory cache
        self.download_memory.cache = blocks_flags_bits

    def final(self):
        # written file final md5 checking
        with open(
                os.path.join(self.download_path, self.__temp_prefix__ % self.name), "rb"
        ) as f:
            not_passed = []
            cur = 0
            for r, md5 in zip(self.conf.md5_check_range, self.conf.md5_array):
                if hashlib.md5(f.read(r)).hexdigest() != md5:
                    not_passed.append(cur)
                cur += r
        if not_passed:
            print(
                "Critical: File<%s> NOT passed through MD5 checking and Failed at %s" % (self.name, not_passed)
            )
        # rename written file
        try:
            os.rename(
                os.path.join(self.download_path, self.__temp_prefix__ % self.name),
                os.path.join(self.download_path, self.conf.filename)
            )
        except FileExistsError:
            os.rename(
                os.path.join(self.download_path, self.__temp_prefix__ % self.name),
                os.path.join(self.download_path, "copy_%s_%s" % (str(time.time()).rsplit(".")[1], self.conf.filename))
            )
        # remove temp files
        for i in self.__remove__:
            prefix = getattr(self, "__%s_prefix__" % i, None)
            if isinstance(prefix, str):
                self.remove(prefix)

    def remove(self, prefix):
        try:
            os.remove(os.path.join(self.download_path, prefix % self.name))
        except FileExistsError as e:
            raise NoLocationErrors(e)

    def __call__(self, max_workers=None, verbose=True):
        print("Configuring ... ...")
        self.resolute_settings_from_conf()

        mod = None
        # If no cache and temp, initial downloading, overwrite everything related to target
        if not(
                os.path.exists(os.path.join(self.download_path, self.__temp_prefix__ % self.name)) and
                os.path.exists(os.path.join(self.download_path, self.__cache_prefix__ % self.name))
        ):
            print("Preparing ... ...")
            mod = "A"
        self.download_initiation(mod)

        print("Loading ... ...")
        self.loading_blocks()
        # Initial Master Downloader targeting to Master server
        master = self.get_abstract_master()
        self.master = self.get_downloader(master)
        self.master.set_source(self.conf.fileid)

        print("Indexing seeds ... ...")
        # Index Seeds Downloader
        self.index_seeds()

        temp = []
        blocks = BLOCKS
        reindex_counts = 0
        max_workers = (max_workers or self.conf.max_workers) + 1
        if not blocks:
            print("Checking ... ...")
            self.final()
            return
        # print(blocks)
        # return
        print("Downloading ... ...")

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            # write threads
            write = pool.submit(self.write, verbose)
            write.add_done_callback(self.get_callback()["writer"])

            # read threads
            while len(blocks) or GDICT["checked"] > status.SUCCEEDED:
                try:
                    temp.append(blocks.pop(0))
                except IndexError:
                    continue
                if len(temp) < max_workers and len(blocks):
                    continue

                MESSAGE_QUEUE.queue("+ Prepared blocks[%s]" % ",".join(temp))
                read_handlers = []
                read_callback = self.get_callback()["reader"]
                for block in temp:
                    read = pool.submit(self.run, block)
                    read.add_done_callback(read_callback)
                    read_handlers.append(read)
                response = map(lambda x: x.result(), as_completed(read_handlers))
                for status_, block in response:
                    if status_ > status.SUCCEEDED:
                        MESSAGE_QUEUE.queue("- Download ErrorCode(%d): block<%s>" % (status_, block))
                        blocks.append(block)
                        # record error times in order to reindex seeds
                        reindex_counts += 1
                if reindex_counts == self.conf.max_reindex:
                    self.index_seeds()
                    reindex_counts = 0
                temp = []
        print()
        print("Checking ... ...")
        self.final()
        print("Done !")


class CourierLauncher(object):

    client_class = None

    def __init__(self, fname: str, path: str, configure: bytes):
        self.fname = fname
        self.path = path
        self.configure = configure

    def get_client_class(self):
        return self.client_class

    def get_client(self):
        return self.client_class(self.fname, download_path=self.path)

    def set_path(self):
        if os.path.exists(self.path):
            # TODO: LOG WARNING
            print("Overwriting Existed Directory!: %s" % self.path)
            return
        try:
            os.makedirs(self.path)
        except Exception as e:
            raise NoLocationErrors(e)

    def initial_configure_file(self):
        with open(os.path.join(self.path, self.fname), "wb") as f:
            f.write(self.configure)

    def response(self, msg):
        return str(msg)

    def __call__(self, **pclient):
        msg = None
        try:
            self.set_path()
            self.initial_configure_file()
            self.get_client()(**pclient)
        except UniErrors as e:
            msg = e
        finally:
            return self.response(msg)


__all__ = ["GenericCourierManager", "CourierLauncher"]
