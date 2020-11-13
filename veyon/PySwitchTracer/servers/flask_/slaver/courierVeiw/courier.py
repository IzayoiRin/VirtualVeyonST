import SwitchTracer as st
from SwitchTracer.cores.contrib.couriermiddlewares.componets.caches import CourierCache
from SwitchTracer.cores.contrib.couriermiddlewares.componets.downloader import CourierDownloader
from SwitchTracer.cores.contrib.couriermiddlewares.componets.abstract_servers import AbstractServer
from SwitchTracer.cores.contrib.couriermiddlewares.componets.callbacks import RaiseOnlyThreadPoolCallback
from SwitchTracer.cores.contrib.couriermiddlewares import status
from SwitchTracer.universal.exceptions import ContentTypeErrors, SerializerSettingErrors, SerializerValidationErrors


class StAbstractServer(AbstractServer):

    def resp_parser(self, response):
        sname = self.kwargs.get("serialize", "bytes")
        mapping = {
            "bytes": response.content,
            "json": response.json,
        }
        serializer = mapping.get(sname)
        if serializer is None:
            raise SerializerSettingErrors("No such builtin serializer<%s>" % sname)
        try:
            return serializer()
        except Exception as e:
            raise ContentTypeErrors(e)


COURIER_MASTER_SERVER = StAbstractServer()


class StCourierDownloader(CourierDownloader):

    def request(self, block: int):
        try:
            json_dict = self.server.connect(purl={"pid": self.source, "bid": block}, serialize="json")
            status_, json_dict = self.validate_fields(json_dict)
        except (ContentTypeErrors, SerializerValidationErrors) as e:
            return status.UNKNOWN, e
        # validation passed
        if status_ == status.SUCCEEDED:
            return status_, json_dict
        elif status_ == status.REFUSED:
            return status_, "Refused: localhost:{remote} request for pack{pid}'s {bid}th block".format(**json_dict)
        else:
            return status.UNKNOWN, str(json_dict)


class StCourierClient(st.courier.GenericCourierManager):

    downloader_class = StCourierDownloader
    cache_class = CourierCache
    abstract_master = COURIER_MASTER_SERVER
    pool_exception_callback = RaiseOnlyThreadPoolCallback


class StCourierLauncher(st.courier.CourierLauncher):

    client_class = StCourierClient

    def response(self, msg):
        if msg:
            return str(msg)
        return "200 ok"
