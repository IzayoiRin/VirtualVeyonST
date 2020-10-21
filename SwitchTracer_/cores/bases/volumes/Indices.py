import pickle

from universal.exceptions import VolumeErrors, RedisOperationErrors


class IndexVolumesBase(object):
    volume_class = None

    def __init__(self, vol, volume_class, _ctype=None):
        if not isinstance(vol.__class__(), volume_class or self.volume_class):
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
                from cores.contrib.celerymiddlewares import set_celery_from_conf
                set_celery_from_conf(self.vol["capp"], env=self.vol.environ)
            return self.vol["capp"].tasks.get(key, ret)


class IndexRedisPools(IndexVolumesBase):

    class RedisPool:

        def __init__(self, **kwargs):
            from universal.tools.functions import connect_redis_pool
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
