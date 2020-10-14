""" There are code for Resoluter"""
import time
import SwitchTracer_ as st
from cores.compents.recorders import Recorder
from cores.compents.registers import Register
from universal.exceptions import SettingErrors, ResoluterErrors
from universal.volumes import Volumes
from multiprocessing import Process

_helper_pool = []


class GenericResoluter:

    recorder_class = None
    register_class = None
    VOLUMES = None
    dynamic_pool_info = None
    _environ = None
    max_pool = 3
    async_helper_prefix = "helper"

    def __init__(self):
        self.kwargs = dict()
        self._dynamic_pool_info = self.dynamic_pool_info or \
                                  st.environ(self._environ).settings.get("DEFAULT_DYNAMIC_POOL_INFO")
        if not isinstance(self._dynamic_pool_info, dict):
            raise SettingErrors("Can Not found dynamic pool info of multiprocessing in settings.RESOLUTER")
        super(GenericResoluter, self).__init__()

    @classmethod
    def _get_records_list(cls):
        return cls.VOLUMES().RECORDS

    @classmethod
    def _get_registers_map(cls):
        return cls.VOLUMES().REGISTERS

    def __str__(self):
        return "@{sender}:<{greg}->{grec}>".format(
            sender=self.__class__.__name__,
            greg=self._get_registers_map().id(),
            grec=self._get_records_list().id()
        )

    def get_register_class(self):
        return self.register_class

    def get_register(self, tskey):
        creg = self.get_register_class()(key=tskey)
        return creg

    def get_records_class(self):
        return self.recorder_class

    def get_records(self, **kwargs):
        return self.get_records_class()(**kwargs)

    def records(self, underflow, timeout, blocked):
        r = self.get_records(
            overflow=0, underflow=underflow, timeout=timeout
        )
        if not blocked:
            r.blocking_off()
        return r

    def _listen(self, pname, grec):
        s = self.dynamic_info(pname, timeout=0)
        s.link_with_records(grec)
        print(s.params())
        if not (s.params()["blocked"] or (s.params()["min"] * 2) < len(s)):
            return
        while s.params()["blocked"] or s.params()["min"] < len(s):
            time.sleep(0.1)
            dequeue = s.pop(0, s.params()["blocked"])
            # blocked mod: pop will not underflow cause timeout=0 repr process No Releasing.
            # Non-blocked mod: pop will underflow and return None value repr the process Terminated.
            if not isinstance(dequeue, int):
                if pname == "main":
                    continue
                else:
                    return
            if not self.polling(dequeue):
                s.push(dequeue + 3, False)

    def polling(self, dequeue):
        # if dequeue.ready():
        #     self.get_register().delay(dequeue.get())
        #     return 1
        if dequeue % 2 == 0:
            return 1
        return 0

    def dynamic_info(self, pname, timeout=1):
        starting = self.kwargs.get(pname) or self._dynamic_pool_info.get(pname)
        is_short_circuit = (isinstance(starting, int) is False)
        underflow = 1 if is_short_circuit else starting // 2
        return self.records(underflow=underflow, blocked=is_short_circuit, timeout=timeout)

    def async_helper(self, monitors, timeout=0.1):
        global _helper_pool
        for idx, hd in enumerate(_helper_pool):
            if hd is None:
                _helper_pool[idx] = Process(
                    target=self._listen,
                    args=("helper%d" % idx, self._get_records_list())
                )
                if len(self._get_records_list()) > monitors[idx]:
                    _helper_pool[idx].start()
            elif hd.is_alive() is False:
                _helper_pool[idx] = None
        if timeout > 0 and all(_helper_pool):
            time.sleep(timeout)

    def async_listen(self, **kwargs):
        self.kwargs = kwargs
        hd0 = Process(
            target=self._listen,
            args=("main", self._get_records_list())
        )
        # hd0.start()
        max_helper_pool = (kwargs.get("max_pool", None) or self.max_pool) - 1
        kwset = {i for i in self.kwargs if i.startswith(self.async_helper_prefix)}
        cfset = set(self._dynamic_pool_info.keys())
        available_helper = kwset.union(cfset)
        if max_helper_pool < 1:
            # TODO: WARNING
            print("Warning: No helper for listening!")
        elif max_helper_pool > len(available_helper):
            raise ResoluterErrors(
                "Numbers of helpers exceed! only %d helpers can be found in settings" % len(available_helper)
            )
        else:
            global _helper_pool
            _helper_pool = [None for _ in range(max_helper_pool)]
            helper_settings = {
                int(k[len(self.async_helper_prefix):]):
                    self.kwargs.get(k, None) or self._dynamic_pool_info.get(k) for k in available_helper
            }
            while True:
                self.async_helper(monitors=helper_settings, timeout=0.1)


class UniResoluter(GenericResoluter):

    recorder_class = Recorder
    register_class = Register


def main():
    from cores.domains.senders import RoutineSenderCenter
    RoutineSenderCenter.VOLUMES = Volumes
    s = RoutineSenderCenter()
    s.async_rec()
    print(s._get_records_list())
    GenericResoluter.VOLUMES = Volumes
    r = GenericResoluter()
    r.async_listen(max_pool=3)
    print(s._get_records_list())
    print(Volumes().RECORDS)
