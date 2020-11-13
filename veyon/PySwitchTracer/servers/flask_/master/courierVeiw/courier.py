import time
import SwitchTracer as st


class StCourierMasterServer(st.courier.CourierMasterServer):

    redis_pool = None
    TOTAL_BLOCKS = 96
    MAX_CONNECTION = 8
    MONITOR_ULRS = {
        "updates": r"/master/updates/(\d+)/(\d+)",
    }

    def read(self, pid: int, bid: int):
        # time.sleep(1)
        return super(StCourierMasterServer, self).read(pid, bid)

    def idempotence_url_updates(self, matched, request):
        pid, bid = matched.groups()
        self.refused_dict["pid"] = pid
        self.refused_dict["bid"] = bid
        self.refused_dict["remote"] = request.remote_addr
