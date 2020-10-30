from flask import Flask

import SwitchTracer_ as st
from universal.tools.functions import import_from_path
from universal.exceptions import SettingErrors


class FlaskApplicationFactory(object):

    prefix = "FLASK"

    def __init__(self, env=None):
        self.environ = env
        self.settings = None
        self.roles = list()
        self.blue_printers = dict()
        self._get_settings()
        self._get_blue_printer()

    def _get_settings(self):
        self.settings = st.environ(self.environ).settings.get(self.prefix, None)
        if self.settings is None:
            raise SettingErrors("Can not find settings.FLASK!")
        if self.settings.get("name") is None:
            self.settings["name"] = "SwitchTracer_"
        self.roles = [i[1:] for i in self.settings.keys() if i.startswith("@")]
        if not self.roles:
            raise SettingErrors("Can not find any ROLEs in settings.FLASK!")

    def _get_blue_printer(self):
        fmod = self.settings.get("server") or \
               st.environ(self.environ).settings["SERVERS"]["flask"]
        try:
            self.blue_printers = {
                i: import_from_path("{flask}.{bprinter}".format(flask=fmod, bprinter=i)).bluePrinters
                for i in self.roles
            }
        except Exception as e:
            raise SettingErrors(e)

    def register_bprinter(self, app, role):
        if role not in self.roles:
            raise SettingErrors("Can not find ROLE<%s> in settings.FLASK!" % role)
        for bp in self.blue_printers[role]:
            app.register_blueprint(bp)

    def __call__(self, role):
        if role not in self.roles:
            raise SettingErrors("Can not find ROLE<%s> in settings.FLASK!" % role)
        role = "@%s" % role
        app = Flask(self.settings["name"])
        app.config.from_mapping(**self.settings[role])
        return app
