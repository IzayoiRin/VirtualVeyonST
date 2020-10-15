def runmonitor(gmap, glist, gdict):
    from cores.domains.resoluters import UniResoluter
    UniResoluter.default_global_registers_map = gmap
    UniResoluter.default_global_records_list = glist
    rst = UniResoluter()
    rst.async_listen(gdict, max_pool=3)
