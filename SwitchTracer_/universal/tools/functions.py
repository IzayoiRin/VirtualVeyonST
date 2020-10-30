import re
import os
import pickle
import base64
from importlib import import_module
import redis

import SwitchTracer_ as st
from universal.exceptions import SettingErrors, ConnectionErrors, ImportedErrors

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


def import_(mod: str, tar):
    try:
        ret = import_module(mod)
    except ModuleNotFoundError:
        if tar is None:
            try:
                mod, tar = mod.rsplit('.', 1)
            except ValueError:
                raise ImportedErrors("<%s> is NOT existed!" % mod)
            return import_(mod, tar)
        else:
            raise ImportedErrors("<%s> is NOT existed!" % mod)
    else:
        ret = getattr(ret, tar, None) if tar else ret
        if ret is None:
            raise ImportedErrors("<%s> does NOT include <%s>" % (mod, tar))
        return ret


def import_from_path(mod: str, raise_=True, return_=None):
    try:
        lib = import_(mod, None)
    except ImportedErrors as e:
        if raise_:
            raise ImportedErrors(e)
        return return_
    return lib


def base64_switcher(mode, encoding="utf-8", return_type=None):
    """
    Base64 switcher with decoder and encoder.
    Example:
        s = base64_switcher("encode", return_type="utf-8")("Base64 coding")
        print(s)
        s = base64_switcher("decode", return_type="utf-8")(s)
        print(s)
    :param mode: options["encode", "decode"]
    :param encoding: string data encoding mode
    :param return_type: return data type, default None repr Bytes, option[None, encoding mode]
    """
    mapping = {"encode": "b64encode", "decode": "b64decode"}
    opt = mapping[mode]

    def base64_(data):
        if not isinstance(data, bytes):
            data = data.encode(encoding)
        ret = getattr(base64, opt)(data)
        return ret if return_type is None else ret.decode(return_type)

    return base64_
