class ThreadPoolCallbackBase(object):

    logger = None
    handlers = ["writer", "reader"]

    def get_logger(self):
        return self.logger

    def decorate_handler(self, item, handler):
        return handler

    def __getitem__(self, item, raise_=False):
        if item in self.handlers and hasattr(self, item):
            return self.decorate_handler(item, getattr(self, item))
        if raise_:
            raise KeyError("Illegal handler: %s" % item)


class GenericThreadPoolCallback(ThreadPoolCallbackBase):

    logger = None

    def writer(self, worker):
        if self.get_exception(worker):
            # TODO: LOGGER
            self.get_logger()

    def reader(self, worker):
        if self.get_exception(worker):
            # TODO: LOGGER
            self.get_logger()

    def get_exception(self, worker):
        worker_exception = worker.exception()
        if worker_exception:
            return worker_exception


class RaiseOnlyMixin(object):

    raises = []

    def decorate_handler(self, item, handler):
        def inner(worker):
            if self.get_exception(worker):
                raise RuntimeError(worker)
        return inner if item in self.raises else handler


class RaiseOnlyThreadPoolCallback(RaiseOnlyMixin, GenericThreadPoolCallback):

    raises = ["writer", "reader"]
    logger = None
