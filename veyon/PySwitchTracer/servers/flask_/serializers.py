from SwitchTracer.cores.contrib.flaskmiddlewares import serializer
from SwitchTracer.universal.tools.functions import base64_switcher


class SdcSerializer(serializer.Serializer):
    x = serializer.Integer()
    # y = serializer.Integer(required=False)


class UpdatesSerializer(serializer.Serializer):
    pid = serializer.Integer()
    bid = serializer.Integer()


class ConfigureSerializer(serializer.Serializer):

    fname = serializer.String(required=True)
    path = serializer.String(required=True, encoding=base64_switcher("decode", return_type="utf-8"))
    configure = serializer.String(required=True, encoding=base64_switcher("decode"))
