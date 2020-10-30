import SwitchTracer_ as st
from SwitchTracer_.cores.contrib.couriermiddlewares.componets.caches import CourierCache
from SwitchTracer_.cores.contrib.couriermiddlewares.componets.downloader import CourierDownloader
from SwitchTracer_.cores.contrib.couriermiddlewares.componets.abstract_servers import AbstractServer


class StCourier(st.courier.GenericCourierManager):

    downloader_class = CourierDownloader
    cache_class = CourierCache
    abstract_master = AbstractServer
