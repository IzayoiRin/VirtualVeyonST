# import requests
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

        self._url = self.get_ulr(self.settings.get("master") or self.url_master)
        self._feedback_url = self.settings.get("seed") or self.url_feedback

    def get_ulr(self, url: str):
        try:
            method, address = url.split(self.__url_split__)
        except AttributeError:
            return
        except (ValueError, TypeError):
            return
        return method, address

    def connect(self, block):
        pass
