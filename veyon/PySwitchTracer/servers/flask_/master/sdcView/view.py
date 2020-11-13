from flask import request

from SwitchTracer.universal.exceptions import SerializerValidationErrors

from servers.flask_.master.sdcView import bp
from servers.flask_.master.sdcView.sdc import SdcFactory, sdcRecorder
from servers.flask_.serializers import SdcSerializer


# TODO: requesting frequency limitations
@bp.route("/sdc/<tasks>", methods=["GET"])
def sdc(tasks):
    reg = "sdc.%s" % tasks
    s = SdcFactory.set_register(reg)
    try:
        query_data = SdcSerializer(request.args).serialize()
        sdcRecorder.push(s.spawn(**query_data))
    except (TypeError, SerializerValidationErrors) as e:
        # TODO: URL FOR Params INNER EXCEPTION BACKENDS
        return "wrong params: %s" % e, 400
    except Exception as e:
        # TODO: URL FOR Universal INNER EXCEPTION BACKENDS
        return "Server Inner Error: %s" % e, 500
    return "hello %s" % reg


@bp.route("/sdc/help", methods=["GET"])
def assistant():
    return "Hello, here is SenderCenter assistant coming from SwitchTracer"
