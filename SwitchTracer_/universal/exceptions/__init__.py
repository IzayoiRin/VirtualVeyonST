class UniErrors(Exception):
    pass


class SetupErrors(UniErrors):
    pass


class SettingErrors(UniErrors):
    pass


class ConfigureSyntaxErrors(UniErrors):
    pass


class NoLocationErrors(UniErrors):
    pass


class ImportedErrors(UniErrors):
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


class ParserSettingErrors(UniErrors):
    pass


class ContentTypeErrors(UniErrors):
    pass
