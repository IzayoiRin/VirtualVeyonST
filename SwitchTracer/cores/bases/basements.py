import os
from importlib import import_module

from SwitchTracer.universal.exceptions import SettingErrors


class Settings(object):

    def __init__(self, setting_module):
        self._settings_module = import_module(setting_module)
        self._settings = dict()

    def lazy(self):
        self.resolute_settings()
        return self

    def resolute_settings(self):
        for k in dir(self._settings_module):
            if k.isupper():
                self._settings[k] = getattr(self._settings_module, k)

    def keys(self):
        return self._settings.keys()

    def items(self):
        return self._settings.items()

    def values(self):
        return self._settings.values()

    def get(self, *args, **kwargs):
        return self._settings.get(*args, **kwargs)

    def __getitem__(self, key):
        v = self._settings.get(key, None)
        if v is None:
            raise SettingErrors("can Not found '%s' in settings" % key)
        return v


class Environ(object):

    def __init__(self, env_key="SwitchTracer_"):
        self.__name = env_key
        self.__settings_module = os.environ.get(env_key)
        if self.__settings_module is None:
            raise EnvironmentError("Setup Global Environ First by calling 'manager.setup()'")
        self.settings = Settings(self.__settings_module).lazy()

    @property
    def name(self):
        return self.__name

    @property
    def settings_module(self):
        return self.__settings_module
