""" There are code for Activator """
import os
import SwitchTracer_ as st

st.DEFAULT_SETTINGS_MODULE = "st_settings.dev.settings"
CHANGE = True
ROLE = "master"


def test():
    from multiprocessing import Process
    from test import test
    hd = Process(target=test, args=(st.VOLUMES.REGISTERS, st.VOLUMES.RECORDS, st.DEFAULT_ENVIRON_KEY))
    hd.start()
    hd.join()


if __name__ == '__main__':
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

    if os.environ.get("FLASK_SETUP"):
        st.setup()
    # setup environ with importing and only set os.env once at first time
    else:
        cur_env = getattr(st, "_environ")

        activator = getattr(st, "activators").Activator(cur_env.name)
        activator.setup_g_volume()
        activator.test_celery_redis_net_link(st.VOLUMES.REDIS)
        activator.setup_g_redis_pool(st.VOLUMES.REDIS)

        os.environ["FLASK_SETUP"] = ROLE
        fapp = activator.setup_flask_application(ROLE)

        test()
        # TODO: INFO MSG
        msg = "+++ Switch Tracer Activated +++\n" \
              "|-Current Environ[{env}] loading from <{mod}>.\n" \
              "|-Current Redis connection: \n{redis}\n" \
              "|-Listen based on FLASK application[{role}]." \
            .format(env=cur_env.name, mod=cur_env.settings_module,
                    redis="\n".join(
                        [" * %s://%s:%s:%s" % (k, v["host"], v["port"], v["db"]) for k, v in st.VOLUMES.REDIS.items()]
                    ),
                    role=ROLE)
        print(msg)
        # fapp.run()
