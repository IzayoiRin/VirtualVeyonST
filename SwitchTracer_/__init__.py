import os
import sys
from importlib import import_module

ROOT_DIR = os.path.dirname(__file__)
DEFAULT_ENVIRON_KEY = os.path.split(ROOT_DIR)[-1]
DEFAULT_SETTINGS_MODULE = "st_settings.dev.settings"


class SetupError(Exception):
    pass


def environ(env_key=None):
    settings = import_module(os.environ.get(env_key or DEFAULT_ENVIRON_KEY))
    return getattr(import_module(settings.KERNELWARES["basements"]), "Environ")(env_key or DEFAULT_ENVIRON_KEY)


def _setup():
    """Setup default environ for SwitchTracer_, including settings, kernel wares"""
    if os.environ.get(DEFAULT_SETTINGS_MODULE, None) is None:
        sys.path.append(ROOT_DIR)
        os.environ[DEFAULT_ENVIRON_KEY] = DEFAULT_SETTINGS_MODULE
    this = sys.modules[__name__]
    getattr(this, "_environ",
            setattr(this, "_environ", environ())
            )
    getattr(this, "_settings",
            setattr(this, "_settings", getattr(this, "_environ").settings)
            )
    kernels = getattr(this, "_settings").get("KERNELWARES")
    for k, v in kernels.items():
        getattr(this, k,
                setattr(this, k, import_module(v))
                )


def re_setup(covered=False, covered_key=None):
    """
    Setup default environ for SwitchTracer_, in covered model or uncovered model
    :param covered_key: only worked in covered model, cover this key with new one.
    :param covered: whether covered model.
    """
    if covered and covered_key is not None:
        try:
            del os.environ[covered_key]
            # TODO: RAISE WARNING MSG
            print("covered the original key: %s " % covered_key)
        except KeyError as e:
            raise SetupError("Can not find and cover the original key: %s" % e)
    os.environ[DEFAULT_ENVIRON_KEY] = DEFAULT_SETTINGS_MODULE
    _setup()


# setup default environ for SwitchTracer_
_setup()
