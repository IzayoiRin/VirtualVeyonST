import os
import pickle

from SwitchTracer.universal.exceptions import NoLocationErrors


class CourierCache(object):

    def __init__(self, cache):
        if not os.path.exists(cache):
            raise NoLocationErrors("Could not find cache<%s>" % cache)
        self.name = cache
        self.__cache = None

    @property
    def cache(self):
        with open(self.name, "rb") as f:
            return pickle.load(f)

    @cache.setter
    def cache(self, cc):
        with open(self.name, "wb") as f:
            pickle.dump(cc, f)
