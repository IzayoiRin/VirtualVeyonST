from flask import request

from SwitchTracer_.cores.contrib.flaskmiddlewares.parser_render import JsonParser

from demo.servers.flask_.slaver.courierVeiw import bp
from demo.servers.flask_.serializers import ConfigureSerializer
from demo.servers.flask_.slaver.courierVeiw.courier import StCourierLauncher

path = r"C:\izayoi\prj_veyon\SwitchTracer\SwitchTracer_\cores\contrib\couriermiddlewares\tests"


@bp.route("/system/updates", methods=["PUT"])
def updates():
    data = JsonParser(request)(encoding="utf-8")
    data = ConfigureSerializer(data).serialize()
    launcher = StCourierLauncher(**data)
    launcher.set_path()
    launcher.get_client()(verbose=True)
    return "ok", 200
