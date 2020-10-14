class UniErrors(Exception):
    pass


class SettingErrors(UniErrors):
    pass


class KernelWaresSettingsErrors(UniErrors):
    pass


class RegisterErrors(UniErrors):
    pass


class ResoluterErrors(UniErrors):
    pass


class VolumeErrors(UniErrors):
    pass


class ConnectionErrors(UniErrors):
    pass


class RedisOperationErrors(UniErrors):
    pass


class SerializerSettingErrors(UniErrors):
    pass


class SerializerValidationErrors(UniErrors):
    pass
