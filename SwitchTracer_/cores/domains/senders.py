import SwitchTracer_ as st
from cores.compents.recorders import Recorder
from cores.compents.registers import _static_register, SdcRegister
from universal.exceptions import SettingErrors, KernelWaresSettingsErrors


class SenderCenterMeta(type):
    __is_single = True

    def __new__(mcs, name, bases, kw_attrs):
        if mcs.__is_single or kw_attrs.get("_is_reload", False):
            kw_attrs["VOLUMES"] = kw_attrs.get("_default_global_volumes") or st.VOLUMES
            settings = st.environ(kw_attrs.get("_environ", None)).settings
            if settings.get("DEFAULT_TASKS_URLS") is None:
                raise SettingErrors("Can not find settings.TASKS refers!")
            kw_attrs["_TASKS"] = kw_attrs.get("_default_tasks_urls") or settings["DEFAULT_TASKS_URLS"]
        mcs.__is_single = False
        kw_attrs["_is_reload"] = False
        return type(name, bases, kw_attrs)


class SenderCenterBase(object, metaclass=SenderCenterMeta):
    _default_global_volumes = None
    _default_tasks_urls = None
    _environ = None
    _gvol = None

    def __new__(cls, *args, **kwargs):
        cls._gvol = getattr(cls, "VOLUMES", None)
        if cls._gvol is None:
            raise KernelWaresSettingsErrors("No VOLUMES has been Linked!")
        return super().__new__(cls)

    @classmethod
    def _get_records_list(cls):
        return cls._gvol.RECORDS

    @classmethod
    def _get_registers_map(cls):
        return cls._gvol.REGISTERS

    @classmethod
    def static_register(cls, *tasks_urls):
        """register tasks from assigned tasks url or module path"""
        print("Warning: REGISTERS Map will be injected manually !")
        for url in tasks_urls:
            _static_register(url, cls._get_registers_map())

    def __init__(self):
        # TODO: SenderCenterBase initial params
        if not self._get_registers_map():
            return
        for url in getattr(self, "_TASKS"):
            _static_register(url, self._get_registers_map())

    @property
    def id(self):
        return hex(id(self))

    def dynamic_register(self, name, task):
        # TODO: Dynamic register core
        pass


class GenericSenderCenter(SenderCenterBase):

    register_class = None
    recorder_class = None

    def __init__(self, factory=False):
        self._rname = None
        self._creg = None
        self.factory = factory
        super().__init__()

    def is_factory(self):
        return self.factory

    def __str__(self):
        return "@{sender}{factory}:<{greg}&&{grec}>".format(
            sender=self.__class__.__name__,
            factory="[Factory]" if self.factory else "",
            greg=self._get_registers_map().id(),
            grec=self._get_records_list().id()
        )

    def load(self, name, fn):
        self.dynamic_register(name=name, task=fn)

    def set_register(self, name):
        if self.factory:
            ins = self.__class__()
            ins._rname = name
            return ins
        self._rname = name
        return self

    def get_register_class(self):
        return self.register_class.link2gvol(self._get_registers_map())

    def get_register(self):
        self._creg = self.get_register_class()(key=self._rname)
        return self._creg

    def spawn(self, *args, **kwargs):
        reg = self.get_register()
        return reg.delay(*args, **kwargs)

    def get_records_class(self):
        return self.recorder_class

    def get_records(self, **kwargs):
        return self.recorder_class(**kwargs)

    def records(self, overflow=100, timeout=1):
        rc = self.get_records(
            overflow=overflow, underflow=0, timeout=timeout
        )
        return rc.link_with_records(self._get_records_list())


class RoutineSenderCenter(GenericSenderCenter):
    register_class = SdcRegister
    recorder_class = Recorder
