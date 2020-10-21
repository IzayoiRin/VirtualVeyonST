def runmonitor(gmap, glist, gdict, env=None):
    from cores.domains.resoluters import UniResoluter
    UniResoluter.default_global_registers_map = gmap
    UniResoluter.default_global_records_list = glist
    rst = UniResoluter(env=env)
    rst.async_listen(gdict)
