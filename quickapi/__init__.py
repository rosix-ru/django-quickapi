VERSION = (2, 5, 1)

def get_version(*args, **kwargs):
    return '.'.join([ str(x) for x in VERSION ])

__version__ = get_version()

default_app_config = 'quickapi.apps.AppConfig'
