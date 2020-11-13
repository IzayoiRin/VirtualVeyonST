from servers.flask_.slaver.receptorView import bp


@bp.route("/receptor", methods=["GET"])
def receptor():
    return "Hello from Receptor"
