import re
from universal.exceptions import SerializerValidationErrors, SerializerSettingErrors


class FieldsType(object):

    _type = None

    def __init__(self, required=True):
        self.required = required

    def check(self, val):
        try:
            v = self._type(val)
        except ValueError:
            return None
        return v


class Integer(FieldsType):
    _type = int


class SerializerBase(object):
    __hidden__ = re.compile(r"^_validator_([a-zA-Z0-9_]+)$")

    def __new__(cls, *args, **kwargs):
        fields = dict()
        for k in dir(cls):
            val = getattr(cls, k)
            if isinstance(val, FieldsType):
                ret = re.match(cls.__hidden__, k)
                if ret is None:
                    setattr(cls, "_validator_%s" % k, val)
                    delattr(cls, k)
                else:
                    k = ret.group(1)
                fields[k] = val
        setattr(cls, "validators", fields)
        return super().__new__(cls)


class Serializer(SerializerBase):

    def __init__(self, data: dict):
        self.data = data
        self._validated = False
        self._data = dict()

    def is_validated(self):
        return self._validated

    @property
    def required_fields(self):
        return {k for k, v in self.validators.items() if v.required}

    def validate(self):
        if self.is_validated():
            return

        assert getattr(self, "validators", None),\
            SerializerSettingErrors("No legal validator has been linked to this serializer!")

        if self.required_fields:
            uni = self.required_fields & set(self.data.keys())
            assert len(uni) == len(self.required_fields), \
                "Lost Value for required filed<%s>" % ",".join(uni ^ self.required_fields)

        for k, v in self.data.items():
            validator = self.validators.get(k)
            assert validator is not None, "Could not find legal validator for Fields<%s>" % k
            v = validator.check(v)
            assert v is not None, "Invalidated Value for Fields<%s>" % k
            self._data[k] = v
        self._validated = True

    def serialize(self, raise_=True):
        try:
            self.validate()
        except AssertionError as e:
            if raise_:
                raise SerializerValidationErrors(e)
            else:
                return None
        return self._data
