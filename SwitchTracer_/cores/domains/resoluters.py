""" There are code for Resoluter"""
import time
from multiprocessing import Process

import SwitchTracer_ as st
from cores.compents.recorders import Recorder
from cores.compents.registers import Register

from universal.exceptions import SettingErrors, ResoluterErrors, KernelWaresSettingsErrors

_helper_pool = []


class ResoluterBase(object):

    default_global_registers_map = None
    default_global_records_list = None

    __dynamic_pool__ = None
    __environ__ = None

    def __init__(self):
        if self.default_global_registers_map is None or self.default_global_records_list is None:
            raise KernelWaresSettingsErrors("No VOLUMES has been Linked!")
        setattr(self, "__REGISTERS", self.default_global_registers_map)
        setattr(self, "__RECORDS", self.default_global_records_list)
        self.__dynamic_pool__ = self.__dynamic_pool__ or \
                               st.environ(self.__environ__).settings.get("DEFAULT_DYNAMIC_POOL_INFO")
        if not isinstance(self.__dynamic_pool__, dict):
            raise SettingErrors("Can Not found dynamic pool info of multiprocessing in settings.RESOLUTER")

    def _get_records_list(self):
        return getattr(self, "__RECORDS")

    def _get_registers_map(self):
        return getattr(self, "__REGISTERS")

    @property
    def id(self):
        return hex(id(self))

    def __str__(self):
        return "@{sender}:<{greg}->{grec}>".format(
            sender=self.__class__.__name__,
            greg=self._get_registers_map().id(),
            grec=self._get_records_list().id()
        )


class GenericResoluter(ResoluterBase):

    recorder_class = None
    register_class = None
    _environ = None
    max_pool = 3
    async_helper_prefix = "helper"

    def __init__(self):
        self.kwargs = dict()
        super(GenericResoluter, self).__init__()

    def get_register_class(self):
        return self.register_class.link2gvol(self._get_registers_map())

    def get_register(self, tskey):
        return self.get_register_class()(key=tskey)

    def get_records_class(self):
        return self.recorder_class

    def get_records(self, **kwargs):
        return self.get_records_class()(**kwargs)

    def records(self, underflow, timeout, blocked):
        recorder = self.get_records(
            overflow=0, underflow=underflow, timeout=timeout
        )
        if not blocked:
            recorder.blocking_off()
        return recorder

    def _listen(self, pname, grec):
        recorder = self.dynamic_recorder(pname, timeout=0)
        recorder.link_with_records(grec)
        params = recorder.params()
        if not (params["blocked"] or (params["min"] * 2) < len(recorder)):
            return
        # print(len(recorder), recorder, params)
        while params["blocked"] or params["min"] < len(recorder):
            time.sleep(0.1)
            dequeue = recorder.pop(0, params["blocked"])
            # blocked mod: pop will not underflow cause timeout=0 repr process No Releasing.
            # Non-blocked mod: pop will underflow and return None value repr the process Terminated.
            if not isinstance(dequeue, int):
                if pname == "main":
                    continue
                else:
                    return
            if not self.polling(dequeue):
                recorder.push(dequeue+3, False)
            # print(recorder)

    def dynamic_recorder(self, pname, timeout=1):
        starting = self.kwargs.get(pname) or self.__dynamic_pool__.get(pname)
        is_short_circuit = (isinstance(starting, int) is False)
        underflow = 1 if is_short_circuit else starting // 2
        return self.records(underflow=underflow, blocked=is_short_circuit, timeout=timeout)

    def polling(self, dequeue):
        # if dequeue.ready():
        #     print(dequeue.get())
        #     # self.get_register().delay(dequeue.get())
        #     return 1
        if dequeue % 2 == 0:
            return 1
        return 0

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

    def async_listen(self, gdict, **kwargs):
        self.kwargs = kwargs
        hd0 = Process(
            target=self._listen,
            args=("main", self._get_records_list())
        )
        hd0.start()
        gdict["pid_main_monitor"] = hd0.pid
        max_helper_pool = (kwargs.get("max_pool", None) or self.max_pool) - 1
        kwset = {i for i in self.kwargs if i.startswith(self.async_helper_prefix)}
        cfset = set(self.__dynamic_pool__.keys())
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
                    self.kwargs.get(k, None) or self.__dynamic_pool__.get(k) for k in available_helper
            }
            while True:
                self.async_helper(monitors=helper_settings, timeout=0.1)


class UniResoluter(GenericResoluter):

    recorder_class = Recorder
    register_class = Register
