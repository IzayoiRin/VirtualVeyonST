import hashlib
import os
import pickle
import re

import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor
from cores.contrib.couriermiddlewares import status
from universal.exceptions import ConfigureSyntaxErrors, SettingErrors, NoLocationErrors

S = "../tests/upload_.txt"
N = 96


class TempMessageQueue(object):
    def __init__(self, mq=None):
        self.mq = mq or list()

    def queue(self, x):
        self.mq.append(x)

    def dequeue(self):
        if self.is_empty():
            return None
        return self.mq.pop(0)

    def is_empty(self):
        return not bool(len(self.mq))

    def iloc_set(self, idx, value):
        self.mq[idx] = value

    def iloc_show(self, filter_=None):
        print("#" * 10, "MESSAGE QUEUE", "#" * 10)
        for i in self.mq:
            if filter_ is None or filter_(i):
                print(i)
        print("#" * 35)

    def queue_show(self, filter_=None):
        print("#" * 10, "MESSAGE QUEUE", "#" * 10)
        while not self.is_empty():
            x = self.dequeue()
            if filter_ is None or filter_(x):
                print(x)
        print("#" * 35)

    def show(self, mod: str, filter_=None):
        show = getattr(self, "%s_show" % mod.lower(), None)
        if show:
            show(filter_)


class MasterSever(object):

    source = S
    TOTAL_BLOCKS = N

    def __init__(self, url=None):
        self.url = url or "GET: localhost/master/udpacks/<id>"
        self.feedback_url = "PUT: localhost/master/seed"
        self.max_connect = 3
        self.X = os.path.getsize(self.source)
        self.storage_per_blocks = np.ceil(self.X / self.TOTAL_BLOCKS).astype(np.int)

    def connect(self, block):
        block = int(block)
        # try to connect target server, request for current connections
        cur_connect = np.random.choice([2, 5], replace=False, p=[0.8, 0.2])
        if cur_connect < self.max_connect:
            with open(self.source, "rb") as f:
                s = min(self.storage_per_blocks, self.X - self.storage_per_blocks * block)
                f.seek(block * self.storage_per_blocks, 0)
                content = f.read(s)
                return status.SUCCEEDED, (content, hashlib.md5(content).hexdigest())
        return status.REFUSED, "Server Busy Now"

    def feedback(self, opt, *blocks):
        return status.SUCCEEDED, "%s: %s with blocks[%s]" % (opt, self.feedback_url, ",".join(blocks))


GDICT = {"checked": status.PREPARED}
MESSAGE_QUEUE = TempMessageQueue()
TASK_QUEUE = TempMessageQueue()
M = MasterSever()
T = time.time()

BLOCKS = []


class Downloader(object):

    def __init__(self, server):
        self.server = server

    @property
    def id(self):
        return hex(id(self))

    def connect(self, block):
        status_, msg = self.server.connect(block)
        if status_ == status.SUCCEEDED:
            # TODO: Download code
            MESSAGE_QUEUE.queue(
                "# Requesting block<%s> at %s" % (block, self.server.url.replace("<id>", block))
            )
            time.sleep(np.random.randint(0, 1) * 0.5)
            TASK_QUEUE.queue((block, msg))
            return status.SUCCEEDED, "Succeeded block<%s>" % block
        return status.PREPARED, msg

    def update_seeds(self, *blocks):
        status_, msg = self.server.feedback("UpdateSeed", *blocks)
        MESSAGE_QUEUE.queue("# BackCode<%d>: %s" % (status_, msg))


class CourierConfigure(object):

    def __getattribute__(self, item):
        try:
            return super(CourierConfigure, self).__getattribute__(item)
        except AttributeError:
            raise SettingErrors("Could not find key<%s> in conf" % item)

    def __str__(self):
        return str({k: getattr(self, k) for k in dir(self) if not k.startswith("_")})

    def __repr__(self):
        return repr({k: getattr(self, k) for k in dir(self) if not k.startswith("_")})


class CourierCache(object):

    def __init__(self, cache):
        if not os.path.exists(cache):
            raise NoLocationErrors("Could not find cache<%s>" % cache)
        self.name = cache
        self.__cache = None

    @property
    def cache(self):
        with open(self.name, "rb") as f:
            return pickle.load(f)

    @cache.setter
    def cache(self, cc):
        with open(self.name, "wb") as f:
            pickle.dump(cc, f)


vacancy_conf = CourierConfigure()


class CourierManager(object):

    downloader_class = Downloader
    master = None
    NULL = b'\x00'

    __conf_prefix__ = ".download_%s.conf"
    __conf_pattern__ = re.compile(r"^(?P<key>[0-9A-Z_]+) = (?P<val>.*)$")
    __temp_prefix__ = "download_%s.temp"
    __cache_prefix__ = "download_%s.cache"

    __verbose__ = {
        status.SUCCEEDED: "\033[0;41m \033[0m",
        status.PREPARED: "\033[0;45m \033[0m",
        status.INFO: '\033[0;33m %s',
    }

    def __init__(self, name: str, download_path=None):
        if not name:
            raise
        self.name = name
        self.download_path = download_path or os.path.dirname(__file__)
        self.conf = vacancy_conf
        self.download_memory = None
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

    def download_initiation(self, mod=None, encoding=None):
        def write(file, func):
            location = os.path.join(self.download_path, file)
            if os.path.exists(location):
                # TODO: LOG WARNING
                print("Overwrite warning: file<%s> has been existed in path<%s>" % (file, self.download_path))
            with open(location, "wb", encoding=encoding) as temp:
                func(temp)

        if mod == "T" or mod == "A":
            vacancy_memory = self.NULL * self.conf.memory
            write(self.__temp_prefix__ % self.name, lambda f: f.write(vacancy_memory))
        if mod == "C" or mod == "A":
            blk_bit_flag = [status.PREPARED for _ in range(self.conf.total_blocks)]
            write(self.__cache_prefix__ % self.name, lambda f: pickle.dump(blk_bit_flag, f))

        self.download_memory = CourierCache(
            os.path.join(self.download_path, self.__cache_prefix__ % self.name)
        )

    def loading_blocks(self):
        global BLOCKS
        # get download memory cache
        blocks_flags_bits = self.download_memory.cache
        BLOCKS = ["%03d" % i for i, s in enumerate(blocks_flags_bits) if s == status.PREPARED]

    def get_downloader_class(self):
        return self.downloader_class

    def get_downloader(self, server):
        return self.downloader_class(server)

    def request(self, block):
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

    def run(self, block):
        retries = self.conf.max_retries
        while retries:
            flag, msg = self.request(block)
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

    def index_seeds(self):
        # indexing from master Redis
        self.seeds = []
        MESSAGE_QUEUE.queue("! Indexing Seed from Redis")

    def write(self, verbose):
        with open(
                os.path.join(self.download_path, self.__temp_prefix__ % self.name), "rb+"
        ) as f:
            print("File<%s> starts at %s" % (self.conf.filename, time.ctime()))
            self._write(buffer=f, verbose=verbose)

    def _write(self, buffer, verbose):
        start = time.time()
        _start_ = start
        checked = self.conf.total_blocks - sum(self.download_memory.cache)
        seeds = []
        while checked < self.conf.total_blocks:
            task = TASK_QUEUE.dequeue()
            if task is None:
                time.sleep(0.5)
                continue
            block, (context, md5) = task
            status_ = self.check_md5(context, md5)
            if status_ > status.SUCCEEDED:
                BLOCKS.append(block)
                MESSAGE_QUEUE.queue("? Check ErrorCode(%d): block<%s>" % (status_, block))
                continue
            # write down
            self.write2file(int(block), context, buffer, verbose=verbose, startime=start)
            MESSAGE_QUEUE.queue("+ Write blocks<%s> Succeeded" % block)
            seeds.append(block)
            if len(seeds) and (
                    len(seeds) > self.conf.upload_frequency[0] or time.time() - _start_ > self.conf.upload_frequency[1]
            ):
                self.master.update_seeds(*seeds)
                MESSAGE_QUEUE.queue("! Upload seeds blocks[%s]" % ",".join(seeds))
                seeds = []
                _start_ = time.time()
            checked += 1
        GDICT["checked"] = status.SUCCEEDED

    def write2file(self, idx, context, buffer, verbose=True, startime=None):
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
                if speed < 1024:
                    unit = ""
                elif speed > 1024:
                    speed /= 1024
                    unit = "K"
                else:
                    speed /= 1024
                    unit = "M"
                times = "-avg.speed: {s} {u}Bytes/s -approximate.last: {l} s".format(
                    s=round(speed, 2), u=unit, l=last
                )
            msg = "\r[%.2f %% %s] %s" % (percent, times, bar)
            print(self.__verbose__.get(status.INFO, ""), msg, end="")
        # overwrite download memory cache
        self.download_memory.cache = blocks_flags_bits

    def check_md5(self, context, md5):
        return status.SUCCEEDED if hashlib.md5(context).hexdigest() == md5 else status.DESTROYED

    def final(self):
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
        os.remove(os.path.join(self.download_path, self.__cache_prefix__ % self.name))
        # os.remove(os.path.join(self.download_path, self.__conf_prefix__ % self.name))

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
        self.master = self.get_downloader(M)

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

        # return
        print("Downloading ... ...")
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            # write threads
            write = pool.submit(self.write, verbose)

            # read threads
            while len(blocks) or GDICT["checked"] > status.SUCCEEDED:
                try:
                    temp.append(blocks.pop(0))
                except IndexError:
                    continue
                if len(temp) < max_workers and len(blocks):
                    continue
                MESSAGE_QUEUE.queue("+ Prepared blocks[%s]" % ",".join(temp))
                response = pool.map(self.run, temp)
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


def main():
    M.source = "../tests/upload_.txt"
    M.TOTAL_BLOCKS = 96
    cm = CourierManager("test", download_path="../tests/")
    np.random.seed(5)
    cm(verbose=True)
    MESSAGE_QUEUE.show("iloc", lambda x: x.startswith("!"))


def set_conf():
    X = os.path.getsize(S)
    per = np.ceil(X / N).astype(np.int)
    rg = np.ceil(X / 3).astype(np.int)
    rga = [rg, rg, X - 2 * rg]
    with open("../tests/upload_.txt", 'rb') as f:
        mds = [hashlib.md5(f.read(i)).hexdigest() for i in rga]
    print(X, N, per, rga, mds)


if __name__ == '__main__':
    # set_conf()
    main()

