from universal.fuc_tools import task_urls_routers
from universal.exceptions import KernelWaresSettingsErrors, RegisterErrors


def _static_register(url: str, gmap: dict, env=None):
    """
    register tasks from static tasks urls
    :param url: "task_module_path<reg-prefixed-file.py>@task_prefix"
    :param gmap: global REGISTERS map
    """
    task_urls_routers(url, records=True, gmap=gmap, env=None)


class RegisterBase(object):

    _env = None

    @classmethod
    def link2gvol(cls, gvol):
        setattr(cls, "__registers", gvol)
        return cls

    def __init__(self, key: str):
        REGISTERS = getattr(self, "__registers")
        if REGISTERS is None:
            raise KernelWaresSettingsErrors("No VOLUMES has been Linked!")
        self.task = self.get_tasks(key)
        if self.task is None:
            raise RegisterErrors("No Register has been found!")

    def get_tasks(self, key):
        raise NotImplementedError

    def delay(self, *args, **kwargs):
        raise NotImplementedError

    def __repr__(self):
        return "<@Register:{}>".format(self.task.name)


class Register(RegisterBase):

    _ctypes = None

    def get_tasks(self, key):
        REGISTERS = getattr(self, "__registers")
        return REGISTERS.indices(self._ctypes)[key]

    def delay(self, *args, **kwargs):
        return self.task.delay(*args, **kwargs)


class SdcRegister(Register):
    _ctypes = "refer"
