import SwitchTracer_ as st
import os


def test(gmap, glist, env_key="Demo"):
    st.DEFAULT_ENVIRON_KEY = env_key
    st.DEFAULT_SETTINGS_MODULE = os.environ["Demo"]
    st.setup()
    # s = gmap.indices(_ctype="pkl")['sdc.move11']
    # print(gmap.id(), s, id(gmap["capp"]))
    # s.delay(2)


# def test_processing():
#     sdc = RoutineSenderCenter()
#     sdc._get_records_list().extend(list(range(21)))
#     # print(id(sdc._get_records_list()))
#     r = RoutineResoluter()
#     r.async_listen()
#     # l = list(range(10))
#     # for _ in range(20):
#     #     dequeue = l.pop(0)
#     #     print(dequeue)
#     #     dequeue += 10
#     #     l.append(dequeue)
#     # print(l)

