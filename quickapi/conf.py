# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings

methods = { 'quickapi.test': 'quickapi.views.test' }

SITE_ID = settings.SITE_ID
DEBUG   = settings.DEBUG

QUICKAPI_DEFINED_METHODS       = getattr(settings, 'QUICKAPI_DEFINED_METHODS', methods)
QUICKAPI_ONLY_AUTHORIZED_USERS = getattr(settings, 'QUICKAPI_ONLY_AUTHORIZED_USERS', False)
QUICKAPI_INDENT                = getattr(settings, 'QUICKAPI_INDENT', 2)
QUICKAPI_DEBUG                 = getattr(settings, 'QUICKAPI_DEBUG', False)
QUICKAPI_SWITCH_LANGUAGE       = getattr(settings, 'QUICKAPI_SWITCH_LANGUAGE', True)
QUICKAPI_SWITCH_LANGUAGE_AUTO  = getattr(settings, 'QUICKAPI_SWITCH_LANGUAGE_AUTO', True)
QUICKAPI_DECIMAL_LOCALE        = getattr(settings, 'QUICKAPI_DECIMAL_LOCALE', False)
QUICKAPI_ENSURE_ASCII          = getattr(settings, 'QUICKAPI_ENSURE_ASCII', False)
