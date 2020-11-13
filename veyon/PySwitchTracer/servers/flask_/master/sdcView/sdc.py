import SwitchTracer as st
from SwitchTracer.cores.domains.senders import RoutineSenderCenter


class StSenderCenter(RoutineSenderCenter):

    VOLUMES = st.VOLUMES


SdcFactory = RoutineSenderCenter(factory=True)
sdcRecorder = SdcFactory.records()
