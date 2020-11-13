from SwitchTracer.cores.bases.volumes.Indices import IndexNull, IndexRegisters, IndexRedisPools


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
        return self.Indices(self, self.__class__, *args, **kwargs)


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
