import os
import SwitchTracer_ as st


capp = st.celerys.routine_app


def organized_by_paths():
    print("Organized by paths")
    dirname = os.path.dirname(__file__)
    st.celerys.organized_urls = [os.path.join(dirname, "task1"), os.path.join(dirname, "task2"), __file__]


def organized_by_urls():
    # organized_urls default load form settings.tasks_urls
    print("Organized by Urls")


# organized_by_paths()
st.celerys.load_tasks_from_organized_urls()
