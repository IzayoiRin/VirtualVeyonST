import pickle
from multiprocessing.managers import BaseManager
from universal.exceptions import VolumeErrors, RedisOperationErrors


class IndexVolumesBase(object):

    def __init__(self, vol, _ctype=None):
        if not isinstance(vol.__class__(), VolumesBase):
            raise VolumeErrors("Link a legal ST Volumes!")
        self.vol = vol
        self._ctype = _ctype or "pkl"


class IndexRegisters(IndexVolumesBase):

    def __getitem__(self, key, ret=None):
        if key not in self.vol.keys():
            return ret
        if self._ctype == "pkl":
            try:
                return pickle.loads(self.vol[key])
            except Exception as e:
                raise VolumeErrors(e)
        if self._ctype == "refer":
            assert self.vol.get("capp") or hasattr(self.vol["capp"], "conf"), \
                VolumeErrors("Indexing from Reference must be linked to a legal Celery.application")
            if self.vol["capp"].conf.broker_url is None:
                from cores.utils.celerys import set_celery_from_conf
                set_celery_from_conf(self.vol["capp"], env=self.vol.environ)
            return self.vol["capp"].tasks.get(key, ret)


class IndexRedisPools(IndexVolumesBase):

    class RedisPool:

        def __init__(self, **kwargs):
            from universal.fuc_tools import connect_redis_pool
            self.redis = connect_redis_pool(**kwargs)

        def __enter__(self):
            return self.redis

        def __exit__(self, exc_type, exc_val, exc_tb):
            # TODO: INFO MSG REDIS POOL CLOSED
            self.redis.close()
            if exc_type:
                raise RedisOperationErrors(exc_val)

        def __repr__(self):
            return self.redis.__repr__()

        def __str__(self):
            return self.redis.__str__()

    def __getitem__(self, key, ret=None):
        if key not in self.vol.keys():
            return ret
        return self.RedisPool(**self.vol[key])


class IndexNull(IndexVolumesBase):

    pass


class VolumesBase(object):

    vinfo = None
    is_instanced = None
    Indices = IndexNull

    def __new__(cls, *args, **kwargs):
        if cls.is_instanced is None:
            cls.is_instanced = super().__new__(cls, *args, **kwargs)
        return cls.is_instanced

    def __init__(self, *args, **kwargs):
        self._environ = None
        self._settings = None

    def setup(self, env=None, **kwargs):
        self._environ = env

    def id(self):
        return hex(id(self))

    def info(self):
        return self.vinfo

    def environ(self):
        return self._environ

    def indices(self, *args, **kwargs):
        return self.Indices(self, *args, **kwargs)


class RegistersMap(VolumesBase, dict):

    vinfo = "GlobalRegistersMap"
    Indices = IndexRegisters


class RecordsList(VolumesBase, list):

    vinfo = "GlobalRecordsList"


class RedisPoolsMap(VolumesBase, dict):
    vinfo = "GlobalRedisPoolsMap"
    Indices = IndexRedisPools


class STDict(VolumesBase, dict):
    vinfo = "GlobalDictForST"


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


class Volumes(VolumesManagerBase):

    __exposed__ = ["__len__", "__getitem__", "__class__", "__iter__", "__setitem__"]
    __loading__ = [RegistersMap, RecordsList, RedisPoolsMap, STDict]
    __linking__ = [("REGISTERS", None), ("RECORDS", None), ("REDIS", None), ("DICT", None)]
