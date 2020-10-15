from multiprocessing.managers import BaseManager

from cores.bases.volumes.global_volumes import VolumesBase
from universal.exceptions import VolumeErrors


class VolumesManagerBase(BaseManager):
    instance = None
    none = dict()
    __exposed__ = None
    __loading__ = None
    __linking__ = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self, *args, **kwargs):
        super(VolumesManagerBase, self).__init__(*args, **kwargs)
        self._environ = None
        if not isinstance(self.__loading__, (list, tuple)):
            raise VolumeErrors("must link to a legal Volume")
        for V in self.__loading__:
            self.loading(V)
        self.start()
        if not (
            isinstance(self.__linking__, list) and isinstance(self.__linking__[0], tuple)
        ):
            raise VolumeErrors(
                "Illegal linking configure, correct list[ tuple('name', dict[params] or none), ...]"
            )
        self.lnvolumes = []
        for idx, (name, params) in enumerate(self.__linking__):
            name = name.upper()
            self.linking(name, self.__loading__[idx].__name__, **(params or self.none))
            self.lnvolumes.append(name)

    def loading(self, V):
        if V.__bases__[0] != VolumesBase:
            raise VolumeErrors("must register a legal Volume as subclass of universal.volumes.VolumesBase")
        exposed = [str(i) for i in dir(V) if not i.startswith('_')]
        if isinstance(self.__exposed__, list):
            exposed.extend(self.__exposed__)
        self.register(V.__name__, V, exposed=exposed)

    def linking(self, name: str, link2: str, **kwargs):
        setattr(self, name, getattr(self, link2)(**kwargs))

    def setup(self, env=None, **kwargs):
        self._environ = env
        for name in self.lnvolumes:
            getattr(self, name).setup(env=self._environ, **kwargs.get(name.lower(), self.none))
