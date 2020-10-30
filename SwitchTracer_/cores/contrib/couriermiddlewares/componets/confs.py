from universal.exceptions import SettingErrors


class UniversalCourierConfigure(object):

    __inner_method_prefix__ = "_"

    def __getattribute__(self, item):
        try:
            return super(UniversalCourierConfigure, self).__getattribute__(item)
        except AttributeError:
            raise SettingErrors("Could not find key<%s> in conf" % item)

    def _lsattrs(self):
        return {k: getattr(self, k) for k in dir(self) if not k.startswith(self.__inner_method_prefix__)}

    def __str__(self):
        return str(self._lsattrs())

    def __repr__(self):
        return repr(self._lsattrs())


vacancy_uniconf = UniversalCourierConfigure()
