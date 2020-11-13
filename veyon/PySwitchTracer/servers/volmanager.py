from SwitchTracer.cores.bases.volumes.global_volumes import RegistersMap, RecordsList, RedisPoolsMap, STDict
from SwitchTracer.cores.bases.volumes.volume_manager import VolumesManagerBase


class Volumes(VolumesManagerBase):

    __exposed__ = ["__len__", "__getitem__", "__class__", "__iter__", "__setitem__"]
    __loading__ = [RegistersMap, RecordsList, RedisPoolsMap, STDict]
    __linking__ = [("REGISTERS", None), ("RECORDS", None), ("REDIS", None), ("DICT", None)]
