# -*- coding: utf-8 -*-
#
#  quickapi/conf.py
#  
#  Copyright 2012 Grigoriy Kramarenko <root@rosix.ru>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
#  
from __future__ import unicode_literals
from django import get_version as django_version
from django.conf import settings

from quickapi import __version__ as QUICKAPI_VERSION

DJANGO_VERSION = django_version()

PROJECT_NAME = getattr(settings, 'PROJECT_NAME', None)
PROJECT_URL  = getattr(settings, 'PROJECT_URL', None)

QUICKAPI_DEFINED_METHODS       = getattr(settings, 'QUICKAPI_DEFINED_METHODS',
                                        {'quickapi.test': 'quickapi.views.test'})
QUICKAPI_ONLY_AUTHORIZED_USERS = getattr(settings, 'QUICKAPI_ONLY_AUTHORIZED_USERS', False)
QUICKAPI_INDENT                = getattr(settings, 'QUICKAPI_INDENT', 2)
QUICKAPI_DEBUG                 = getattr(settings, 'QUICKAPI_DEBUG', False)
QUICKAPI_SWITCH_LANGUAGE       = getattr(settings, 'QUICKAPI_SWITCH_LANGUAGE', True)
QUICKAPI_SWITCH_LANGUAGE_AUTO  = getattr(settings, 'QUICKAPI_SWITCH_LANGUAGE_AUTO', True)
QUICKAPI_DECIMAL_LOCALE        = getattr(settings, 'QUICKAPI_DECIMAL_LOCALE', False)
QUICKAPI_ENSURE_ASCII          = getattr(settings, 'QUICKAPI_ENSURE_ASCII', False)
QUICKAPI_MAIL_ADMINS_ERROR_400 = getattr(settings, 'QUICKAPI_MAIL_ADMINS_ERROR_400', False)
QUICKAPI_MAIL_ADMINS_ERROR_405 = getattr(settings, 'QUICKAPI_MAIL_ADMINS_ERROR_405', False)
QUICKAPI_MAIL_ADMINS_ERROR_500 = getattr(settings, 'QUICKAPI_MAIL_ADMINS_ERROR_500', False)
