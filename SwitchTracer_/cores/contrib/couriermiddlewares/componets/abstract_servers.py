import requests

import SwitchTracer_ as st
from universal.exceptions import SettingErrors


class AbstractServer(object):

    url_master = None  # type:str
    url_feedback = None  # type:str
    __prefix__ = "COURIER"
    __url_split__ = "@"

    def __init__(self, env=None):
        self.environ = env
        self.settings = st.environ(self.environ).settings.get(self.__prefix__, None)
        if self.settings is None:
            raise SettingErrors("Can not find settings.COURIER!")
        # TODO: get redis pool
        self.redis_pool = None

        self.url = self.get_ulr(self.settings.get("master") or self.url_master)
        self.fburl = self.settings.get("seed") or self.url_feedback
        self.kwargs = dict()

    def get_ulr(self, url: str):
        try:
            method, address = url.split(self.__url_split__)
        except AttributeError:
            return
        except (ValueError, TypeError):
            return
        return method, address

    def connect(self, purl: dict = None, query_dict: dict = None, data: dict = None, **kwargs):
        self.kwargs = kwargs
        method, url = self.url
        try:
            url = url.format(**(purl or dict()))
        except (IndexError, KeyError):
            raise SettingErrors("Wrong url params from settings.COURIER.")
        sender = getattr(requests, method.lower())
        if sender is None:
            raise SettingErrors("No such Http request method<%s>." % method)
        return self.resp_parser(
            sender(url=url, params=query_dict, data=data or dict())
        )

    def resp_parser(self, response):
        return response.content()

    def upload_seeds(self, seeds):
        # TODO: Real processor for seed updating
        processed = ["seeds<%d-%d>" % (seed["pid"], seed["bid"]) for seed in seeds]
        return 0, "Save to redis: %s" % ",".join(processed)
