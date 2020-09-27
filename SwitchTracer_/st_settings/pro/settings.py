LOG_LEVEL = "WARNING"

""" KERNEL WARES"""
KERNELS = {
    "basements": "universal.basements",
    "cores": "cores",
}

""" Global Volumes """
DEFAULT_REGISTERS_MAP = "test._globals.REGISTERS"
DEFAULT_RECORDS_LIST = "test._globals.RECORDS"

""" Registered Tasks"""
DEFAULT_TASKS_URLS = ["test.tasks.task", "test.tasks.task2@tk"]
DEFAULT_TASK_PREFIX = "task"

""" Config for Celery """
CELERY = {
    # redis://:password@hostname:port/db_number
    "Redis": {
        "broker_url": "redis://:asdlllasd@172.25.1.100:6379/0",
        "result_backend": "redis://:asdlllasd@172.25.1.100:6379/1"
    },
}
