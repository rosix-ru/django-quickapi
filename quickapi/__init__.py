VERSION = (3, 0, 2)

def get_version(*args, **kwargs):
    return '%d.%d.%d' % VERSION

__version__ = get_version()

default_app_config = 'quickapi.apps.AppConfig'
