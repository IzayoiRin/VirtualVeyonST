from cores.contrib.flaskmiddlewares import serializer


class SdcSerializer(serializer.Serializer):
    x = serializer.Integer()
    # y = serializer.Integer(required=False)
