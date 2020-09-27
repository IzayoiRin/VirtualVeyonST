LOG_LEVEL = "DEBUGS"

""" KERNEL WARES"""
KERNELWARES = {
    "basements": "universal.basements",
    "celerys": "cores.utils.celerys",
    "volumes": "universal.volumes"
}

""" Config for Celery """
CELERY = {
    "routine_name": "SwitchTracer_",
    "tasks_search_pattern": r"^(([_a-zA-Z0-9\.]+\.)?task[_a-zA-Z0-9]*).py$",
    # redis://:password@hostname:port/db_number
    "Redis": {
        "broker_url": "redis://:asdlllasd@172.25.1.100:6379/0",
        "result_backend": "redis://:asdlllasd@172.25.1.100:6379/1"
    },
}

""" Registered Tasks"""
DEFAULT_TASKS_ROOT = r"C:/izayoi/prj_veyon/SwitchTracer"
DEFAULT_TASKS_URLS = ["test.tasks.task1<task.*>", "test.tasks.task2<task.*>@tk", "test.tasks.tasks_test3"]
DEFAULT_TASKS_PREFIX = "task"
