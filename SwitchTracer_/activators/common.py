import os
import re
from multiprocessing import Process

import SwitchTracer_ as st
from universal.exceptions import SettingErrors


class Activator(object):

    # "redis://:asdlllasd@172.25.1.18:6379/0"
    celery_url_pattern = re.compile(
        r"^redis://:(?P<pwd>[^@]*)@?(?P<host>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(?P<port>\d+)/?(?P<dbn>\d+)?$"
    )

    def __init__(self, env=None):
        self._environ = env
        self.settings = st.environ(env).settings
        self.broker_url, self.backend_url = None, None
        self.get_settings()

    def resolute_redis_url(self, url):
        ret = re.match(self.celery_url_pattern, url)
        if ret is None:
            raise SettingErrors("Illegal Redis url in settings!")
        return ret.groupdict()

    @staticmethod
    def connect_redis(gredis, name: str, **kwargs):
        gredis[name] = kwargs
        with gredis.indices()[name] as r:
            r.ping()

    def get_settings(self):
        celery_settings = self.settings["CELERY"]
        try:
            rds = celery_settings["Redis"]
            broker = rds["broker_url"]
            backend = rds["result_backend"]
        except KeyError as e:
            raise SettingErrors(e)
        self.broker_url = self.resolute_redis_url(broker)
        self.backend_url = self.resolute_redis_url(backend)

    def test_celery_redis_net_link(self, gredis):
        br, ba = self.broker_url, self.backend_url
        self.connect_redis(
            gredis, "broker",
            host=br["host"], port=br["port"],
            password=br.get("pwd"), db=br.get("dbn", 0), decode_responses=True
        )
        if br["host"] != ba["host"] or br["port"] != ba["port"] or br.get("dbn", 0) != ba.get("dbn", 0):
            self.connect_redis(
                gredis, "backend",
                host=ba["host"], port=ba["port"],
                password=ba.get("pwd"), db=ba.get("dbn", 0), decode_responses=True
            )

    def setup_g_redis_pool(self, gredis):
        self.connect_redis(
            gredis, "common",
            host=self.broker_url["host"], port=self.broker_url["port"],
            password=self.broker_url.get("pwd"), db=10, decode_responses=True
        )

    def setup_g_volume(self, **kwargs):
        from servers.volmanager import Volumes
        st.VOLUMES = Volumes()
        st.VOLUMES.setup(env=self._environ, **kwargs)
        import celery
        st.VOLUMES.REGISTERS["capp"] = celery.app.app_or_default(st.celerys.routine_app)
        st.VOLUMES.DICT["pid_server"] = os.getpid()
        st.VOLUMES.DICT["pid_volumes"] = st.VOLUMES._process.pid

    def setup_flask_application(self, role):
        flask_app_factor = getattr(st, "flasks").FlaskApplicationFactory(env=self._environ)
        fapp = flask_app_factor(role)
        flask_app_factor.register_bprinter(fapp, role=role)
        return fapp

    @staticmethod
    def setup_resoluter_monitor(gdict):
        from servers.resoluter import runmonitor
        # st.VOLUMES.RECORDS.extend(list(range(20)))
        hd = Process(target=runmonitor, args=(st.VOLUMES.REGISTERS, st.VOLUMES.RECORDS, st.VOLUMES.DICT))
        hd.start()
        gdict["pid_resoluter"] = hd.pid
        # hd.join()
