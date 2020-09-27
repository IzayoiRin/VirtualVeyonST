class Volumes(object):

    info = None
    is_instanced = None

    def __new__(cls, *args, **kwargs):
        if cls.is_instanced is None:
            cls.is_instanced = super().__new__(cls, *args, **kwargs)
        return cls.is_instanced

    @property
    def id(self):
        return hex(id(self))


class RegistersMap(dict, Volumes):

    info = "GlobalRegistersMap"


class RecordsList(list, Volumes):

    info = "GlobalRecordsList"


REGISTERS = RegistersMap()
RECORDS = RecordsList()
