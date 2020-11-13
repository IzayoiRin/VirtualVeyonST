import os
import re
import sys

from importlib import import_module
from celery import Celery
import SwitchTracer as st

from SwitchTracer.universal.tools.functions import task_urls_routers
from SwitchTracer.universal.exceptions import SettingErrors

IS_PATH = re.compile(r'[\/\\]')


def _get_celery_settings(env):
    settings = st.environ(env).settings.get("CELERY", None)
    if settings is None:
        raise SettingErrors("Can not find settings.CELERY!")
    return settings


def set_celery_from_conf(capp=None, broker="Redis", env=None, _return=False):
    settings = _get_celery_settings(env)
    broker = settings.get(broker, None)
    if broker is None:
        raise SettingErrors("No such broker!")

    capp = capp or Celery(settings.get("routine_name", "SwitchTracer"))
    capp.conf.broker_url = broker["broker_url"]
    capp.conf.result_backend = broker["result_backend"]
    if _return:
        return capp


def load_tasks_from_path(packs, reset=False, env=None):
    settings = _get_celery_settings(env)
    package_path = os.path.dirname(packs)
    # print(package_path)
    is_organized = eval(os.environ.get("CELERY_ORGANIZED", "0"))
    if reset or (not is_organized):
        # TODO: RAISE INFO MSG
        print("Info: Insert TaskPackage into sys.path")
        sys.path.append(package_path)
    searching = settings.get("tasks_search_pattern")
    if searching is None:
        raise SettingErrors("No tasks search pattern!")
    # r"^(([_a-zA-Z0-9\.]+\.)?task[_a-zA-Z0-9]*).py$"
    pattern = re.compile(searching)

    def _import(x):
        ret = re.match(pattern, x)
        if ret:
            import_module(ret.group(1))

    if os.path.isdir(packs):
        for i in os.listdir(packs):
            _import(".".join([os.path.split(packs)[-1], i]))
    else:
        for i in os.listdir(package_path):
            _import(i)

    os.environ["CELERY_ORGANIZED"] = "1"


def load_tasks_from_urls(url, env=None):
    task_urls_routers(url, records=False, env=env)


def init_organized_urls():
    st.celery.organized_urls = st.environ().settings["DEFAULT_TASKS_URLS"].copy()


def load_tasks_from_organized_urls(env=None):
    init_organized_urls()
    for i in st.celery.organized_urls:
        if re.search(IS_PATH, i):
            load_tasks_from_path(i, env=env)
        else:
            load_tasks_from_urls(i, env)
