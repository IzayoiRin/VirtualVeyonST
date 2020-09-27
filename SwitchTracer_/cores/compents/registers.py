import SwitchTracer_ as st
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
    _default_registers_map_module = None
    _default_registers_map = None
    _env = None

    def __new__(cls, *args, **kwargs):
        setattr(cls, "__registers", getattr(st.volumes, "REGISTERS"))
        return super().__new__(cls)

    def __init__(self, key: str):
        rgmap = getattr(self, "__registers")  # type: dict
        if rgmap is None:
            raise KernelWaresSettingsErrors("No REGISTERS Map has been found!")

        self.task = rgmap.get(key, None)
        if self.task is None:
            raise RegisterErrors("No Register has been found!")

    def delay(self, *args, **kwargs):
        raise NotImplementedError

    def __str__(self):
        return "<@Register:{}>".format(self.task.name)


class Register(RegisterBase):

    def delay(self, *args, **kwargs):
        return self.task.delay(*args, *kwargs)
