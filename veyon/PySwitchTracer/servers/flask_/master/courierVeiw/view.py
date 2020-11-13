from flask import request

from SwitchTracer.cores.contrib.flaskmiddlewares.parser_render import JsonRender, JsonParser
from SwitchTracer.universal.exceptions import NoLocationErrors

from servers.flask_.master.courierVeiw import bp
from servers.flask_.master.courierVeiw.courier import StCourierMasterServer
from servers.flask_.serializers import UpdatesSerializer


@bp.route("/updates/<int:pid>/<int:bid>", methods=["GET"])
def updates(pid, bid):
    # TODO: Token checking
    token = request.cookies.get("allowedToken")
    data = UpdatesSerializer({"pid": pid, "bid": bid}).serialize()
    server = StCourierMasterServer()
    try:
        resp_dict = server.read(**data)
    except NoLocationErrors as e:
        return "404 No Found: %s" % e, 404
    response = JsonRender(**resp_dict)(status="200 ok")
    return response


@bp.route("/updates/temps", methods=["DEL"])
def clear():
    StCourierMasterServer().clear()
    return "ok", 200


@bp.route("/updates/seeds", methods=["PUT"])
def seeds():
    data = JsonParser(request)(encoding="utf-8")
    # TODO: serializer
    return "Update seeds: %s" % data


@bp.before_request
def before():
    refused_dict = StCourierMasterServer().idempotence_diffusion(request)
    if refused_dict:
        response = JsonRender(**refused_dict)(status="403 Refused")
        return response


@bp.teardown_request
def teardown(error):
    StCourierMasterServer().idempotence_precipitation()
    return error
