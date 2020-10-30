from flask import request

from demo.servers.flask_.slaver.courierVeiw import bp


@bp.route("/system/updates", method=["PUT"])
def updates():
    return request.url
