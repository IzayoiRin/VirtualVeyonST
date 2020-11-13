""" Here are code for Activator manger """
import os
import sys
import time
import fire

# <editor-fold desc="Insert custom Framework root path to sys.path">
FRAMEWORK_ROOT = framework_root = os.path.split(sys.path[0])[0]  # for the site-packages path
if FRAMEWORK_ROOT not in sys.path:
    sys.path.insert(0, FRAMEWORK_ROOT)
os.environ["ST_FRAMEWORK_ROOT"] = FRAMEWORK_ROOT
# </editor-fold>

st = None
DEFAULT_ENVIRON_KEY = "SwitchTracer"
DEFAULT_SETTINGS_MODULE = "PySwitchTracer.settings.dev"
ROLE = None
LOADING_SHOCK = 0
TASKS_ORGANIZER = "PySwitchTracer.tasks.organizer"
REQUIREMENTS = "st_requirements.devel"


def commands(exec, env=None, settings=None, role="master", tasks=None, loglevel="INFO", shock="0.4"):
    """
    Switch Tracer Server Manager @copyrights IzayoiRin
    :param exec: execution options [runserver, ...]
    :param env: [uppercase] environ key for running settings
    :param settings: [pymodule_path] module path for running settings
    :param role: [lowercase] identity for running, default "master"
    :param shock: [second] short shock time waiting whole processing on
    :param tasks: registered tasks' organizer
    """
    def runserver():
        global st
        import SwitchTracer as st
        st.DEFAULT_ENVIRON_KEY = env.upper() if env else DEFAULT_ENVIRON_KEY
        st.DEFAULT_SETTINGS_MODULE = settings or DEFAULT_SETTINGS_MODULE
        global ROLE, LOADING_SHOCK
        ROLE, LOADING_SHOCK = role, eval(str(shock))

    def installdevel():
        import time
        print("Install Dependency ... ... %s" % time.ctime())
        if not os.path.exists(REQUIREMENTS):
            raise FileNotFoundError("Could not find Installation Requirements:\n %s" % os.path.abspath(REQUIREMENTS))
        os.system("pip install -r %s" % REQUIREMENTS)
        raise SystemExit("Done! %s" % time.ctime())

    def runcelery():
        os.environ["ST_CELERY_SETUP"] = settings or DEFAULT_SETTINGS_MODULE
        import time
        print("Install Dependency ... ... %s" % time.ctime())
        os.system("celery -A %s worker --loglevel=%s" % (tasks or TASKS_ORGANIZER, loglevel))
        del os.environ["ST_CELERY_SETUP"]
        raise SystemExit("Done! %s" % time.ctime())

    mapping = {
        "runserver": runserver,
        "installdevel": installdevel,
        "runcelery": runcelery,
    }

    if exec not in mapping.keys():
        raise SystemExit("use `python manager.py runserver --params` to start servers")
    mapping[exec]()


if __name__ == '__main__':
    fire.Fire(commands)
    if os.environ.get(st.DEFAULT_ENVIRON_KEY) is None:
        # setup default environ for SwitchTracer
        st.setup()
        # signed current environment
        os.environ["ST_CURRENT_ENV"] = st.DEFAULT_ENVIRON_KEY

    # setup environ with importing and only set os.env once at first time
    cur_env = getattr(st, "_environ")

    # <editor-fold desc="Start your custom Activator">
    """ Here Start your custom Activator """
    # construct activators for prj.SwitchTracer on current environment
    activator = getattr(st, "activator")(cur_env.name)
    # setup global volume, include REGISTERS, RECORDS, REDIS, DICT
    activator.setup_g_volume()
    # download_ redis connection used in Celery broker or backend
    activator.test_celery_redis_net_link(st.VOLUMES.REDIS)
    # setup and download_ connection for Routine redis
    activator.setup_g_redis_pool(st.VOLUMES.REDIS)
    # setup Flask application on current environment
    fapp = activator.setup_flask_application(ROLE)
    # setup & start Resoluter to monitor RECORDS
    activator.setup_resoluter_monitor(st.VOLUMES.DICT)
    """ Activator End """
    # </editor-fold>

    # short shock for loading multi-processor
    time.sleep(LOADING_SHOCK)

    # TODO: INFO MSG
    msg = "+++ Switch Tracer Activated [copyright@IzayoiRin] +++\n" \
          "|-Current Environ[{env}] loading from <{mod}>.\n{pid}\n" \
          "|-Current Redis connection: \n{redis}\n" \
          "|-Listen based on FLASK application[{role}]." \
        .format(env=cur_env.name, mod=cur_env.settings_module,
                pid="\n".join(
                    [" * %s:%d" % (k, v) for k, v in st.VOLUMES.DICT.items() if k.startswith("pid_")]),
                redis="\n".join(
                    [" * %s://%s:%s:%s" % (k, v["host"], v["port"], v["db"]) for k, v in st.VOLUMES.REDIS.items()]),
                role=ROLE)
    print(msg)
    # Flask Server start
    fapp.run(host=fapp.config.get("HOST"), port=fapp.config.get("PORT"))
