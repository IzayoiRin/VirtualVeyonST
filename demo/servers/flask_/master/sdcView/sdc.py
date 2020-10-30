import SwitchTracer_ as st
from SwitchTracer_.cores.domains.senders import RoutineSenderCenter


class StSenderCenter(RoutineSenderCenter):

    VOLUMES = st.VOLUMES


SdcFactory = RoutineSenderCenter(factory=True)
sdcRecorder = SdcFactory.records()
