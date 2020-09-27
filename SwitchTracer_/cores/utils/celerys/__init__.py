import SwitchTracer_ as st
from .cel_tools import *


organized_urls = st.environ().settings["DEFAULT_TASKS_URLS"].copy()
routine_app = set_celery_from_conf(_return=True)
