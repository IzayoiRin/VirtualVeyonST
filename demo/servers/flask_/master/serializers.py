from cores.contrib.flaskmiddlewares import serializer


class SdcSerializer(serializer.Serializer):
    x = serializer.Integer()
    # y = serializer.Integer(required=False)


class UpdatesSerializer(serializer.Serializer):
    pid = serializer.Integer()
    bid = serializer.Integer()
