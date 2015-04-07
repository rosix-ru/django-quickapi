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

from django.conf import settings
from django.utils import six
from django.utils.encoding import force_text


def parse_auth(request, data):
    if request.META.has_key('HTTP_AUTHORIZATION'):
        key = request.META['HTTP_AUTHORIZATION']
    elif request.META.has_key('HTTP_X_AUTHORIZATION'):
        key = request.META['HTTP_X_AUTHORIZATION']
    else:
        return data.get('username', None), data.get('password', None)

    if key.lower().count('basic'):
        if six.PY3:
            b = bytes(key[6:], settings.DEFAULT_CHARSET).decode('base64_codec')
        else:
            b = bytes(key[6:]).decode('base64')

        return force_text(b).split(':')
    else:
        return None, None


def clean_kwargs(request, data):
    kwargs = {}

    for key in data.keys():

        if '[]' in key and (data is request.POST or data is request.GET):
            kwargs[key.replace('[]', '')] = data.getlist(key)

        elif key not in ('method', 'username', 'password', 'language'):
            kwargs[key] = data.get(key)

    return kwargs


def clean_uri(request):
    return request.build_absolute_uri().split(request.path)[0] + request.path


def warning_auth_in_get(request):
    if request.method == 'GET':
        return bool('username' in request.GET or 'password' in request.GET)
    return False

