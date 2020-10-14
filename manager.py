""" There are code for Activator """
import os
import time
import SwitchTracer_ as st

st.DEFAULT_SETTINGS_MODULE = "st_settings.dev.settings"
CHANGE = True
ROLE = "master"


if __name__ == '__main__':

    def resoluter():
        from multiprocessing import Process
        from demo2 import test
        # st.VOLUMES.RECORDS.extend(list(range(20)))
        hd = Process(target=test, args=(st.VOLUMES.REGISTERS, st.VOLUMES.RECORDS, st.VOLUMES.DICT))
        hd.start()
        st.VOLUMES.DICT["pid_resoluter"] = hd.pid
        time.sleep(0.4)
        return hd

    if os.environ.get(st.DEFAULT_ENVIRON_KEY) is None:
        # setup default environ for SwitchTracer_
        st.setup()
    # TODO: COMMANDS LINE
    if CHANGE:
        # change running global environ with resetup
        old_env_key = st.DEFAULT_ENVIRON_KEY
        st.DEFAULT_ENVIRON_KEY = "DEMO"
        st.DEFAULT_SETTINGS_MODULE = "demo.settings"
        st.re_setup(covered=True, covered_key=old_env_key)

    if os.environ.get("ST_CURRENT_ENV") is None:
        os.environ["ST_CURRENT_ENV"] = st.DEFAULT_ENVIRON_KEY

    # setup environ with importing and only set os.env once at first time
    cur_env = getattr(st, "_environ")

    activator = getattr(st, "activators").Activator(cur_env.name)
    activator.setup_g_volume()
    activator.test_celery_redis_net_link(st.VOLUMES.REDIS)
    activator.setup_g_redis_pool(st.VOLUMES.REDIS)
    fapp = activator.setup_flask_application(ROLE)
    hd = resoluter()
    # hd.join()
    # TODO: INFO MSG
    msg = "+++ Switch Tracer Activated +++\n" \
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
    fapp.run()
