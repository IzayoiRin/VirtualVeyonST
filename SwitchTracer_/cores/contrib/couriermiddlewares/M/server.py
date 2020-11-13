import hashlib
import re
from flask import g

import SwitchTracer_ as st
from cores.contrib.couriermiddlewares import status
from cores.contrib.couriermiddlewares.M.models import ServerPackJsonModel
from cores.contrib.couriermiddlewares.utills import AtomicVolume
from universal.exceptions import SettingErrors
from universal.tools.functions import base64_switcher

# counts, version
CONNECTIONS = AtomicVolume(vol=[1, 0])


class CourierMasterServer(object):
    redis_pool = None
    STATIC_MODEL = None
    MAX_CONNECTION = 4
    MONITOR_ULRS = dict()
    prefix = "COURIER"
    refused_dict = {"status": status.REFUSED}

    def __init__(self, env=None):
        self.environ = env
        self.STATIC_MODEL = self.STATIC_MODEL or self.settings.get("sources")
        self.source_model = self.connect2json_static()

    @property
    def settings(self):
        settings = st.environ(self.environ).settings.get(self.prefix)
        if settings is None:
            raise SettingErrors("Can not find settings.COURIER!")
        return settings

    def connect2json_static(self):
        ServerPackJsonModel.connect2static(self.STATIC_MODEL)
        return ServerPackJsonModel()

    def clear(self):
        CONNECTIONS.reset()

    def read(self, pid: int, bid: int):
        # get pack location through pid
        pack = self.source_model.get(pid)
        # read block of pack through bid
        with open(pack.loc, "rb") as f:
            s = min(pack.spb, pack.mem - pack.spb * bid)
            f.seek(pack.spb * bid, 0)
            content = f.read(s)
            return {
                "status": status.SUCCEEDED,
                "content": base64_switcher("encode", return_type="utf-8")(content),
                "md5": hashlib.md5(content).hexdigest(),
                "encoding": "base64",
            }

    def upload_seeds(self, *seeds):
        """
        :param seeds: [{"pid": seed_pid<int>, "bid": seed_bin<int>}, ... ,]
        """
        # TODO: Real processor for seed updating
        processed = ["seeds<%d-%d>" % (seed["pid"], seed["bid"]) for seed in seeds]
        return status.SUCCEEDED, "Save to redis: %s" % ",".join(processed)

    def is_monitored(self, request):
        for key, url_patter in self.MONITOR_ULRS.items():
            matched = re.match(url_patter, request.path)
            if matched:
                return key, matched
        return

    def idempotence_diffusion(self, request):
        monitored = self.is_monitored(request)
        if monitored is None:
            return
        # idempotence add current connection counts
        status_ = self.version_optimistic_lock()
        # whether return refused response
        if status_ > status.SUCCEEDED:
            processor = getattr(self, "idempotence_url_%s" % monitored[0])
            if callable(processor):
                processor(monitored[1], request)
            g.refused = True
            return self.refused_dict

    def version_optimistic_lock(self):
        counts, version = CONNECTIONS.volume
        if counts > self.MAX_CONNECTION:
            return status.REFUSED
        return CONNECTIONS.write(self.add_connections, args=(version+1,), protected=True)

    def add_connections(self, vol, version):
        if version > vol[1]:
            vol[0] += 1
            vol[1] = version
            return status.SUCCEEDED
        return self.version_optimistic_lock()

    def remove_connections(self, vol):
        vol[0] -= 1
        return status.SUCCEEDED

    def idempotence_precipitation(self):
        if getattr(g, "refused", False):
            return
        # non-idempotence remove current connection counts
        CONNECTIONS.write(self.remove_connections, protected=False)


__all__ = ["CourierMasterServer", ]
