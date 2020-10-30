import time
import numpy as np

from cores.contrib.couriermiddlewares import status
from cores.contrib.couriermiddlewares.S.main import TASK_QUEUE
from cores.contrib.couriermiddlewares.utills import MESSAGE_QUEUE


class CourierDownloader(object):

    def __init__(self, server):
        self.server = server

    @property
    def id(self):
        return hex(id(self))

    def connect(self, block):
        status_, msg = self.server.connect(block)
        if status_ == status.SUCCEEDED:
            # TODO: Download code
            MESSAGE_QUEUE.queue(
                "# Requesting block<%s> at %s" % (block, self.server.url.replace("<id>", block))
            )
            time.sleep(np.random.randint(0, 1) * 0.5)
            TASK_QUEUE.queue((block, msg))
            return status.SUCCEEDED, "Succeeded block<%s>" % block
        return status.PREPARED, msg

    def update_seeds(self, *blocks):
        status_, msg = self.server.feedback("UpdateSeed", *blocks)
        MESSAGE_QUEUE.queue("# BackCode<%d>: %s" % (status_, msg))
