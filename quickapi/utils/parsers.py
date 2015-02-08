# -*- coding: utf-8 -*-
#
#  quickapi/utils/parsers.py
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

        if '[]' in key and data is request.POST:
            kwargs[key.replace('[]', '')] = data.getlist(key)

        elif key not in ('method', 'username', 'password'):
            kwargs[key] = data.get(key)

    return kwargs
