from flask import Blueprint
import SwitchTracer_ as st
from cores.domains.senders import RoutineSenderCenter

bp = Blueprint("master", __name__, url_prefix="/master")

RoutineSenderCenter.VOLUMES = st.VOLUMES
SdcFactory = RoutineSenderCenter(factory=True)
recorder = SdcFactory.records()


from . import views
