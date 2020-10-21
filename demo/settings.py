LOG_LEVEL = "DEBUGS"

""" Kernel engines """
KERNEL_ENGINES = {
    "basements": "cores.bases.basements",
    "activator": "cores.activators.common.Activator",
    "celery": "cores.contrib.celerymiddlewares",
    "flask": "cores.contrib.flaskmiddlewares",
    "courier": "cores.contrib.couriermiddlewares",
}

""" Server location """
SERVERS = {
    "volmanager": "demo.servers.volmanager.Volumes",
    "resoluter": "demo.servers.resoluter.runmonitor",
    "flask": "demo.servers.flask_",
}

""" Resoluter """
# <editor-fold desc="Resoluter reger">
DEFAULT_MAX_POOL = 1
DEFAULT_DYNAMIC_POOL_INFO = {"helper0": 40, "helper1": 100}
# </editor-fold>

""" Configure for Celery """
CELERY = {
    "routine_name": "SwitchTracer_",
    "tasks_search_pattern": r"^(([_a-zA-Z0-9\.]+\.)?task[_a-zA-Z0-9]*).py$",
    # redis://:password@hostname:port/db_number
    "Redis": {
        "broker_url": "redis://:asdlllasd@172.25.1.18:6379/0",
        "result_backend": "redis://:asdlllasd@172.25.1.18:6379/1"
    },
}

""" Registered Tasks """
# <editor-fold desc="Registered Tasks refer">
DEFAULT_TASKS_ROOT = r"C:/izayoi/prj_veyon/SwitchTracer"
DEFAULT_TASKS_URLS = ["demo.tasks.task1<task.*>", "demo.tasks.task2<task.*>@tk", "demo.tasks.tasks_test3"]
DEFAULT_TASKS_PREFIX = "task"
# </editor-fold>

""" Configure for Flask """
FLASK = {
    "name": "SwitchTracer_",
    "@master": {
        "DEBUG": False,
        "HOST": "172.25.1.1",
        "PORT": 5000
    },
    # "@slaver": {
    #
    # }
}
