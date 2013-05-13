from django.conf import settings

methods = { 'test': 'quickapi.views.test' }

QUICKAPI_DEFINED_METHODS = getattr(settings, 'QUICKAPI_DEFINED_METHODS', methods)
QUICKAPI_ONLY_AUTHORIZED_USERS = getattr(settings, 'QUICKAPI_ONLY_AUTHORIZED_USERS', False)
QUICKAPI_INDENT = getattr(settings, 'QUICKAPI_INDENT', 2)
