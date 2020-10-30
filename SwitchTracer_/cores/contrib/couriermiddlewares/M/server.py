import os
import hashlib
import re
import time

import numpy as np
from flask import g

from cores.contrib.couriermiddlewares import status
from cores.contrib.couriermiddlewares.utills import AtomicVolume
from universal.exceptions import NoLocationErrors
from universal.tools.functions import base64_switcher

TEMP_PACK_JSON = {
    "100": r"C:\izayoi\prj_veyon\SwitchTracer\SwitchTracer_\cores\contrib\couriermiddlewares\tests\Test_LiSao_context.txt"
}

CONNECTIONS = AtomicVolume(vol=[0, 0])


class CourierMasterServer(object):
    redis_pool = None
    TOTAL_BLOCKS = 96
    MAX_CONNECTION = 4
    MONITOR_ULRS = dict()
    refused_dict = {"status": status.REFUSED}

    def clear(self):
        CONNECTIONS.reset()

    def read(self, pid: int, bid: int):
        time.sleep(1)
        # get pack location through pid
        pack = TEMP_PACK_JSON.get(str(pid))
        if pack is None or os.path.exists(pack) is False:
            raise NoLocationErrors("Could not find pack<%s>" % pid)
        # read block of pack through bid
        X = os.path.getsize(pack)
        storage_per_blocks = np.ceil(X / self.TOTAL_BLOCKS).astype(np.int)
        with open(pack, "rb") as f:
            s = min(storage_per_blocks, X - storage_per_blocks * bid)
            f.seek(storage_per_blocks * bid, 0)
            content = f.read(s)
            return {
                "status": status.SUCCEEDED,
                "content": base64_switcher("encode", return_type="utf-8")(content),
                "md5": hashlib.md5(content).hexdigest(),
                "encoding": "base64",
            }

    def upload_seed(self, *seeds):
        """
        :param seeds: [{"pid": seed_pid<int>, "bid": seed_bin<int>}, ... ,]
        """
        # TODO: Real processor for seed updating
        processed = ["seeds<%d-%d>" % (seed["pid"], seed["bid"]) for seed in seeds]
        return "Save to redis: %s" % ",".join(processed)

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
