import re
import os
import pickle
from importlib import import_module
import redis

import SwitchTracer_ as st
from universal.exceptions import SettingErrors, ConnectionErrors

PATTERN = re.compile(r"^(?P<prefix>[0-9a-zA-Z_.]+)(\<(?P<mprefix>[^<^>]+)\>)?(\@(?P<fprefix>[0-9a-zA-Z_]+))?$")


def task_urls_routers(url, records=True, gmap=None, root=None, env=None):
    settings = st.environ(env).settings
    if not (settings.get("DEFAULT_TASKS_PREFIX") and settings.get("DEFAULT_TASKS_ROOT")):
        raise SettingErrors("Can not find settings.TASKS refers!")

    temp = re.match(PATTERN, url)
    if temp is None:
        return

    router_dict = temp.groupdict()
    prefix, mprefix, fprefix = router_dict["prefix"], \
                               router_dict["mprefix"], \
                               router_dict["fprefix"] or st.environ(env).settings["DEFAULT_TASKS_PREFIX"]
    root = root or st.environ(env).settings["DEFAULT_TASKS_ROOT"]
    _imported_list = list()
    if mprefix:
        for i in os.listdir(os.path.join(root, *prefix.split('.'))):
            ret = re.match("(%s)\.py" % mprefix, i)
            if ret:
                _imported_list.append(import_module(".".join([prefix, ret.group(1)])))
    else:
        _imported_list.append(import_module(prefix))

    def _import(p):
        for k in filter(lambda x: x.startswith(fprefix), dir(p)):
            task = getattr(p, k)
            gmap[task.name] = pickle.dumps(task)

    if records and hasattr(gmap, "__setitem__"):
        for i in _imported_list:
            _import(i)


def connect_redis_pool(**kwargs):
    pool = redis.ConnectionPool(**kwargs)
    rds = redis.Redis(connection_pool=pool)
    try:
        rds.ping()
    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
        raise ConnectionErrors(e)
    return rds
