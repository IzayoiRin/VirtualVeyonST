from flask import request

from universal.exceptions import SerializerValidationErrors
from . import bp, SdcFactory, recorder
from .serializers import SdcSerializer


# TODO: requesting frequency limitations
@bp.route("/sdc/<tasks>", methods=["GET"])
def sdc(tasks):
    reg = "sdc.%s" % tasks
    s = SdcFactory.set_register(reg)
    try:
        query_data = SdcSerializer(request.args).serialize()
        recorder.push(s.spawn(**query_data))
    except (TypeError, SerializerValidationErrors) as e:
        # TODO: URL FOR Params INNER EXCEPTION BACKENDS
        return "wrong params: %s" % e, 400
    except Exception as e:
        # TODO: URL FOR Universal INNER EXCEPTION BACKENDS
        return "Server Inner Error: %s" % e, 500
    return "hello %s" % reg
