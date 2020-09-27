import os
import SwitchTracer_ as st
from cores.domains.senders import RoutineSenderCenter
from cores.compents.registers import _static_register, Register


def setup_and_resetup():
    # setup environ with importing and only set os.env once at first time
    cur_env = getattr(st, "_environ")
    print(cur_env.name, cur_env.settings_module)

    # change running global environ with resetup
    st.DEFAULT_ENVIRON_KEY = "ST"
    st.DEFAULT_SETTINGS_MODULE = "st_settings.pro.settings"
    old_env_key = "SwitchTracer_"
    st.re_setup(covered=True, covered_key=old_env_key)

    cur_env = getattr(st, "_environ")
    print(cur_env.name, cur_env.settings_module)
    print(os.environ.get(st.DEFAULT_ENVIRON_KEY), os.environ.get(old_env_key))


def celery_refer():
    capp = st.celerys.routine_app
    print(capp.main)
    print(capp.tasks.keys())
    import sys
    sys.path.pop(0)
    from demo.tasks import organizer
    print(capp.tasks.keys())


def registers_refer():
    for url in st.environ().settings["DEFAULT_TASKS_URLS"]:
        _static_register(url, st.volumes.REGISTERS)
    print(Register("sdc.move11"))


def sender_center_refer():
    sdc1 = RoutineSenderCenter().set_register("sdc.move11")
    sdc2 = RoutineSenderCenter().set_register("sdc.move21")
    print(sdc1)
    print(sdc2)


def test_run():
    sdc = RoutineSenderCenter().set_register("sdc.move21")
    with sdc.records(timeout=1, overflow=3) as s:
        for i in range(10):
            print(i)
            s.push(sdc.spawn(i))


if __name__ == '__main__':
    # setup_and_resetup()
    # celery_refer()
    registers_refer()
    sender_center_refer()
    test_run()
