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

import json

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.utils import six
from django.utils.encoding import force_text


def parse_auth(request, data):
    """
    Производит поиск авторизационных данных, возвращает кортеж из двух
    элементов: username и password.
    """
    if 'HTTP_AUTHORIZATION' in request.META:
        key = request.META['HTTP_AUTHORIZATION']
    elif 'HTTP_X_AUTHORIZATION' in request.META:
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


def login_from_request(request, data=None):
    """
    Авторизует пользователя извлекая учётные значения из запроса
    или переданного словаря данных. 
    """
    if data is None:
        if 'HTTP_AUTHORIZATION' in request.META or 'HTTP_X_AUTHORIZATION' in request.META:
            data = {}
        else:
            if request.method == 'GET':
                REQUEST = request.GET
            else:
                REQUEST = request.POST

            if 'method' in REQUEST:
                data = REQUEST
            elif 'jsonData' in request.POST:
                try:
                    data = json.loads(REQUEST.get('jsonData'))
                except:
                    return False
            else:
                return False

    username, password = parse_auth(request, data)
    user = authenticate(username=username, password=password)

    if user is not None and user.is_active:
        login(request, user)
        return True

    return False



def clean_kwargs(request, data):
    """
    Очищает данные запроса от зарезервированных ключей.
    """
    kwargs = {}

    for key in data.keys():

        if '[]' in key and (data is request.POST or data is request.GET):
            kwargs[key.replace('[]', '')] = data.getlist(key)

        elif key not in ('method', 'username', 'password', 'language'):
            kwargs[key] = data.get(key)

    return kwargs


def clean_uri(request):
    """
    Очищает путь от параметров GET-запроса, оставляя только сам адрес.
    """
    return request.build_absolute_uri().split(request.path)[0] + request.path


def warning_auth_in_get(request):
    """
    Проверка наличия данных авторизации в GET-запросах.
    Выполняется с кешированием проверки в атрибут `_warning_auth_in_get`
    запроса.
    """
    if request.method != 'GET':
        return False

    if hasattr(request, '_warning_auth_in_get'):
        return request._warning_auth_in_get

    request._warning_auth_in_get = bool('username' in request.GET or 'password' in request.GET)

    return request._warning_auth_in_get


def is_callable(request):
    """
    Проверка вызова метода.

    Когда в POST запросе есть ключ 'jsonData' или 'method', то это вызов метода.
    Когда в GET запросе есть ключ 'method', то это тоже вызов метода.
    Иначе - это просмотр документации.
    """
    if request.method == 'GET':
        if 'method' in request.GET:
            return True
    else:
        req = request.POST
        if 'jsonData' in req or 'method' in req:
            return True

    return False



