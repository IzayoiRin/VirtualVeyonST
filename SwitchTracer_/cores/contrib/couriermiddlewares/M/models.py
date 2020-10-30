import redis

from universal.exceptions import ConnectionErrors, ConfigureSyntaxErrors


class KeyType(object):
    __type__ = None
    __raise_redis_exception__ = True

    @classmethod
    def exception_cather_decorator(cls, func):
        def inner(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
                if self.__raise_redis_exception__:
                    raise ConnectionErrors(e)
                return None
        return inner

    def __new__(cls, *args, **kwargs):
        for method in dir(cls):
            if method.startswith("r_"):
                setattr(cls, method, cls.exception_cather_decorator(getattr(cls, method)))
        return super().__new__(cls)

    def __init__(self, name, is_aio=True):
        self._name = name
        self.is_aio = is_aio
        self.redis = None  # type: redis.Redis

    def link2redis(self, rds: redis.Redis):
        self.redis = rds

    def name(self, **name):
        if not self.is_aio:
            return self._name
        return self._name.format(**name)


class KeySet(KeyType):
    __type__ = set


class KeyHash(KeyType):
    __type__ = dict


class KeyList(KeyType):
    __type__ = list
    __raise_redis_exception__ = False

    def r_index(self, idx, **name):
        return self.redis.lindex(self.name(**name), idx)

    def r_set(self, idx, val, **name):
        self.redis.lset(self.name(**name), idx, val)

    @KeyType.exception_cather_decorator
    def set_many(self, idx, vals=(), keys=()):
        for val, name in zip(vals, keys):
            self.r_set(idx, val, **name)

    @KeyType.exception_cather_decorator
    def index_many(self, idx, keys=()):
        return [self.r_index(idx, **name) for name in keys]


class RedisModels(object):

    addresses = KeyList("SIPAddresses")
    pack_info = KeyHash("Pack_{name}", is_aio=True)

    def __new__(cls, *args, **kwargs):
        fields = {k: v for k, v in cls.__dict__.items() if isinstance(v, KeyType)}
        for k in fields:
            delattr(cls, k)
        setattr(cls, "fields", fields)
        return super().__new__(cls)

    def __init__(self, rds, rds_pool=True):
        self.redis = redis.Redis(connection_pool=rds) if rds_pool else rds  # type: redis.Redis

    def _checking(self):
        try:
            self.redis.ping()
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            raise ConnectionErrors(e)
        if hasattr(self, "fields") and isinstance(self.fields, dict) and self.fields:
            for ktype in self.fields.values():
                ktype.link2redis(self.redis)
        else:
            raise ConfigureSyntaxErrors()

    def iloc(self, field: str, idx: int, key=None, filter_=None):
        field = self.fields.get(field)
        if field is None:
            return
        result = field.index_many(idx, key) \
            if isinstance(key, (list, tuple)) else \
            field.r_index(idx, **(key or dict()))
        return filter_(result) if callable(filter_) else result

    def iset(self, field: str, idx: int, key=None):
        field = self.fields.get(field)
        if field is None:
            return
        if isinstance(key, (list, tuple)):
            field.set_many(idx, key)
        field.r_set(idx, **(key or dict()))

    def kloc(self):
        pass

    def kset(self):
        pass
