from SwitchTracer.cores.contrib.couriermiddlewares import status
from SwitchTracer.cores.contrib.couriermiddlewares.utills import MESSAGE_QUEUE, TASK_QUEUE
from SwitchTracer.universal.exceptions import SerializerValidationErrors


class CourierDownloader(object):

    __required_fields__ = ["content", "md5", "encoding"]

    def __init__(self, server):
        self.server = server
        self.source = None

    def set_source(self, source):
        self.source = source

    @property
    def id(self):
        return hex(id(self))

    def request(self, block: int):
        raise NotImplementedError

    def connect(self, block: int):
        status_, msg = self.request(block)
        if status_ == status.SUCCEEDED:
            MESSAGE_QUEUE.queue(
                "# Requesting block<%s> at %s" % (block, self.server.url)
            )
            TASK_QUEUE.queue((block, msg))
            return status.SUCCEEDED, "Succeeded block<%s>" % block
        return status.PREPARED, msg

    def validate_fields(self, msg: dict):
        status_ = msg.get("status")
        if status_ is None:
            raise SerializerValidationErrors("Lost require field<status> in json response.")
        if status_ == status.SUCCEEDED:
            for field in self.__required_fields__:
                if msg.get(field) is None:
                    raise SerializerValidationErrors("Lost require field<%s> in json response." % field)
        del msg["status"]
        return status_, msg

    def update_seeds(self, *blocks):
        # blocks = [str, str, ...]
        seeds = [{"pid": int(self.source), "bid": int(block)} for block in blocks]
        status_, msg = self.server.upload_seeds(seeds)
        MESSAGE_QUEUE.queue("# BackCode<%d>: %s" % (status_, msg))
