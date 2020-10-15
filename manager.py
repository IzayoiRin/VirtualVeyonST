""" Here are code for Activator manger """
import os
import time
import fire
import SwitchTracer_ as st

DEFAULT_ENVIRON_KEY = "SwitchTracer_"
DEFAULT_SETTINGS_MODULE = "st_settings.dev.settings"
ROLE = None
LOADING_SHOCK = 0


def commands(run, env=None, settings=None, role="master", shock="0.4"):
    """
    Switch Tracer Server Manager @copyrights IzayoiRin
    :param env: [uppercase] environ key for running settings
    :param settings: [pymodule_path] module path for running settings
    :param role: [lowercase] identity for running, default "master"
    :param shock: [second] short shock time waiting whole processing on
    """
    if run != "run":
        raise SystemExit("use `python manager.py run --params` to start servers")
    st.DEFAULT_ENVIRON_KEY = env.upper() if env else DEFAULT_ENVIRON_KEY
    st.DEFAULT_SETTINGS_MODULE = settings or DEFAULT_SETTINGS_MODULE
    global ROLE, LOADING_SHOCK
    ROLE, LOADING_SHOCK = role, eval(str(shock))


if __name__ == '__main__':
    fire.Fire(commands)
    if os.environ.get(st.DEFAULT_ENVIRON_KEY) is None:
        # setup default environ for SwitchTracer_
        st.setup()
        # signed current environment
        os.environ["ST_CURRENT_ENV"] = st.DEFAULT_ENVIRON_KEY

    # setup environ with importing and only set os.env once at first time
    cur_env = getattr(st, "_environ")

    # <editor-fold desc="Start your custom Activator">
    """ Here Start your custom Activator """
    # construct activators for prj.SwitchTracer on current environment
    activator = getattr(st, "activator").Activator(cur_env.name)
    # setup global volume, include REGISTERS, RECORDS, REDIS, DICT
    activator.setup_g_volume()
    # test redis connection used in Celery broker or backend
    activator.test_celery_redis_net_link(st.VOLUMES.REDIS)
    # setup and test connection for Routine redis
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
    fapp.run()
