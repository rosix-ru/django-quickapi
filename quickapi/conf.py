# -*- coding: utf-8 -*-
#
#   Copyright 2012-2015 Grigoriy Kramarenko <root@rosix.ru>
#
#   This file is part of QuickAPI.
#
#   QuickAPI is free software: you can redistribute it and/or
#   modify it under the terms of the GNU Affero General Public License
#   as published by the Free Software Foundation, either version 3 of
#   the License, or (at your option) any later version.
#
#   QuickAPI is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public
#   License along with QuickAPI. If not, see
#   <http://www.gnu.org/licenses/>.
#

from __future__ import unicode_literals
from django import get_version as django_version
from django.conf import settings

from quickapi import __version__ as QUICKAPI_VERSION

DJANGO_VERSION = django_version()

PROJECT_NAME = getattr(settings, 'PROJECT_NAME', None)
PROJECT_URL  = getattr(settings, 'PROJECT_URL', None)

QUICKAPI_DEFINED_METHODS       = getattr(settings, 'QUICKAPI_DEFINED_METHODS', {})
QUICKAPI_ONLY_AUTHORIZED_USERS = getattr(settings, 'QUICKAPI_ONLY_AUTHORIZED_USERS', False)
QUICKAPI_INDENT                = getattr(settings, 'QUICKAPI_INDENT', 2)
QUICKAPI_DEBUG                 = getattr(settings, 'QUICKAPI_DEBUG', False)
QUICKAPI_SWITCH_LANGUAGE       = getattr(settings, 'QUICKAPI_SWITCH_LANGUAGE', True)
QUICKAPI_SWITCH_LANGUAGE_AUTO  = getattr(settings, 'QUICKAPI_SWITCH_LANGUAGE_AUTO', True)
QUICKAPI_DECIMAL_LOCALE        = getattr(settings, 'QUICKAPI_DECIMAL_LOCALE', False)
QUICKAPI_ENSURE_ASCII          = getattr(settings, 'QUICKAPI_ENSURE_ASCII', False)
QUICKAPI_CONTENT_COMPRESS      = getattr(settings, 'QUICKAPI_CONTENT_COMPRESS', False)
QUICKAPI_PYGMENTS_STYLE        = getattr(settings, 'QUICKAPI_PYGMENTS_STYLE', 'default')

QUICKAPI_VERSIONS = getattr(settings, 'QUICKAPI_VERSIONS', {
    'django': DJANGO_VERSION,
    'quickapi': QUICKAPI_VERSION,
    'jquery': '2.1.4',
    'jquery.json': '2.5.1',
    'bootstrap': '3.3.5.quickapi',
    'font-awesome': '4.4.0',
    'pygments': '2.0',
})
