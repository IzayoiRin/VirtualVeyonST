import sys
import os
if os.environ.get("ST_FRAMEWORK_ROOT") and os.environ["ST_FRAMEWORK_ROOT"] not in sys.path:
    sys.path.insert(0, os.environ["ST_FRAMEWORK_ROOT"])

import SwitchTracer as st

capp = st.celery.routine_app


def organized_by_paths():
    print("Organized by paths")
    dirname = os.path.dirname(__file__)
    st.celery.organized_urls = [os.path.join(dirname, "task1"), os.path.join(dirname, "task2"), __file__]


def organized_by_urls():
    # organized_urls default load form settings.tasks_urls
    print("Organized by Urls")


# organized_by_paths()
st.celery.load_tasks_from_organized_urls()
