import SwitchTracer_ as st
from cores.compents.recorders import Recorder
from cores.compents.registers import _static_register, Register
from universal.exceptions import SettingErrors, KernelWaresSettingsErrors


class SenderCenterMeta(type):
    __is_single = True

    def __new__(mcs, name, bases, kw_attrs):
        if mcs.__is_single or kw_attrs.get("_is_reload", False):
            kw_attrs["__registers"] = kw_attrs.get("_default_registers_map") or getattr(st.volumes, "REGISTERS")
            if kw_attrs["__registers"] is None:
                raise KernelWaresSettingsErrors("No REGISTERS Map has been found!")

            settings = st.environ(kw_attrs.get("_environ", None)).settings

            if settings.get("DEFAULT_TASKS_URLS") is None:
                raise SettingErrors("Can not find settings.TASKS refers!")

            for url in kw_attrs.get("_default_tasks_urls") or settings["DEFAULT_TASKS_URLS"]:
                _static_register(url, kw_attrs["__registers"])

            kw_attrs["__records"] = kw_attrs.get("_default_records_list") or getattr(st.volumes, "RECORDS")
            if kw_attrs["__records"] is None:
                raise KernelWaresSettingsErrors("No RECORDS List has been found!")

        mcs.__is_single = False
        kw_attrs["_is_reload"] = False
        return type(name, bases, kw_attrs)


class SenderCenterBase(object, metaclass=SenderCenterMeta):
    _default_registers_map = None
    _default_records_list = None
    _default_tasks_urls = None
    _environ = None

    def __new__(cls, *args, **kwargs):
        rgmap = cls._get_registers_map()
        if rgmap is None:
            raise KernelWaresSettingsErrors("No REGISTERS Map has been found!")
        recls = cls._get_records_list()
        if recls is None:
            raise KernelWaresSettingsErrors("No RECORDS List has been found!")
        return super().__new__(cls)

    def __init__(self):
        # TODO: SenderCenterBase initial params
        pass

    @classmethod
    def _get_registers_map(cls):
        return getattr(cls, "__registers")

    @classmethod
    def _get_records_list(cls):
        return getattr(cls, "__records")

    @classmethod
    def static_register(cls, *tasks_urls):
        """register tasks from assigned tasks url or module path"""
        print("Warning: REGISTERS Map will be injected manually !")
        for url in tasks_urls:
            _static_register(url, cls._get_registers_map())

    def dynamic_register(self, name, task):
        # TODO: Dynamic register core
        pass


class GenericSenderCenter(SenderCenterBase):
    register_class = None
    recorder_class = None

    # metaclass=SenderCenterMeta
    _is_reload = False

    def __init__(self):
        self._rname = None
        self._creg = None
        super().__init__()

    def __str__(self):
        return "@{sender}:{creg}<{greg}->{grec}>".format(
            sender=self.__class__.__name__,
            creg=self.get_register().task.name,
            greg=self._get_registers_map().id,
            grec=self._get_records_list().id
        )

    def load(self, name, fn):
        self.dynamic_register(name=name, task=fn)

    def set_register(self, name):
        self._rname = name
        return self

    def get_register_class(self):
        return self.register_class

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
        return self.get_records(
            records=self._get_records_list(),
            overflow=overflow, timeout=timeout
        )


class RoutineSenderCenter(GenericSenderCenter):
    register_class = Register
    recorder_class = Recorder
