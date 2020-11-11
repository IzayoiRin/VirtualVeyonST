# LOG_LEVEL = "DEBUGS"
#
# """ KERNEL WARES"""
# KERNELWARES = {
#     "basements": "cores.bases.basements",
#     "celerymiddlewares": "cores.contrib.celerymiddlewares",
#     "flasks": "cores.contrib.flaskmiddlewares",
#     "activator": "activators.common",
# }
#
# """ Configure for Celery """
# CELERY = {
#     "routine_name": "SwitchTracer_",
#     "tasks_search_pattern": r"^(([_a-zA-Z0-9\.]+\.)?task[_a-zA-Z0-9]*).py$",
#     # redis://:password@hostname:port/db_number
#     "Redis": {
#         "broker_url": "redis://:asdlllasd@172.25.1.18:6379/0",
#         "result_backend": "redis://:asdlllasd@172.25.1.18:6379/1"
#     },
# }
#
# """ Configure for Flask """
# FLASK = {
#     "name": "SwitchTracer_",
#     "server": "servers.flaskmiddlewares",
#     "@master": {
#         "DEBUG": False,
#         "HOST": "127.0.0.1",
#         "PORT": 5000
#     },
#     "@slaver": {
#
#     }
# }
#
# """ Registered Tasks"""
# DEFAULT_TASKS_ROOT = r"C:/izayoi/prj_veyon/SwitchTracer"
# DEFAULT_TASKS_URLS = ["demo.tasks.task1<task.*>", "demo.tasks.task2<task.*>@tk", "demo.tasks.tasks_test3"]
# DEFAULT_TASKS_PREFIX = "task"
#
# """ Resoluter Refer"""
# DEFAULT_MAX_POOL = 3
# DEFAULT_DYNAMIC_POOL_INFO = {"helper0": 64, "helper1": 256}
