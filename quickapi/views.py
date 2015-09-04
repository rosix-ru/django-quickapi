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
import logging
import decimal
import json

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import six
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.translation import get_language, ugettext_lazy as _

from quickapi import conf
from quickapi.decorators import api_required
from quickapi.http import JSONResponse, JSONRedirect, MESSAGES
from quickapi.utils.method import get_methods
from quickapi.utils.doc import apidoc_lazy, string_lazy
from quickapi.utils.lang import switch_language
from quickapi.utils.requests import (parse_auth, login_from_request,
    clean_kwargs, clean_uri, warning_auth_in_get, is_callable)

logger = logging.getLogger('django.quickapi')

@api_required(ajax_get=True, not_ajax_get=True)
def test(request, code=200, redirect='/'):
    """
    Test response
    """

    try:
        code = int(code)
    except:
        code = 200

    if code in (301, 302):
        return JSONRedirect(location=redirect, status=code,
                message=_('Test response. Redirect to %s.') % redirect)
    elif code == 400:
        return JSONResponse(status=400, message=force_text(_('Test response. Error %d.')) % 400)
    elif code == 500:
        return JSONResponse(status=500, message=_('Test response. Error %d.') % 500)

    now = timezone.now()

    data = {
        'REMOTE_ADDR': request.META.get("HTTP_X_REAL_IP", request.META.get("REMOTE_ADDR", None)),
        'REMOTE_HOST': request.META.get("REMOTE_HOST", None),
        'default language': settings.LANGUAGE_CODE,
        'request language': get_language(),
        'is_authenticated': request.user.is_authenticated(),
        'types': {
            'string': _('String in your localization'),
            'datetime': now,
            'date': now.date(),
            'time': now.time(),
            'decimal': decimal.Decimal('12345678.90'),
            'float': 12345678.90,
            'integer': 1234567890,
        },
        'settings': _('Hidden in not debug mode'),
    }
    if settings.DEBUG:
        data['settings'] = {
            'QUICKAPI_DEFINED_METHODS': conf.QUICKAPI_DEFINED_METHODS,
            'QUICKAPI_ONLY_AUTHORIZED_USERS': conf.QUICKAPI_ONLY_AUTHORIZED_USERS,
            'QUICKAPI_INDENT': conf.QUICKAPI_INDENT,
            'QUICKAPI_DEBUG': conf.QUICKAPI_DEBUG,
            'QUICKAPI_SWITCH_LANGUAGE': conf.QUICKAPI_SWITCH_LANGUAGE,
            'QUICKAPI_SWITCH_LANGUAGE_AUTO': conf.QUICKAPI_SWITCH_LANGUAGE_AUTO,
            'QUICKAPI_DECIMAL_LOCALE': conf.QUICKAPI_DECIMAL_LOCALE,
            'QUICKAPI_ENSURE_ASCII': conf.QUICKAPI_ENSURE_ASCII,
            'QUICKAPI_PYGMENTS_STYLE': conf.QUICKAPI_PYGMENTS_STYLE,
            'QUICKAPI_VERSIONS': conf.QUICKAPI_VERSIONS
        }
    return JSONResponse(data)

test.__doc__ = apidoc_lazy(
    header=_("""Test response."""),
    params=string_lazy(
"""
    1. "code" - %(co)s (%(nr)s);
    2. "redirect"  - %(re)s (%(nr)s).
""", {
    'co': _('code'),
    're': _('address for redirect'),
    'nr': _('not required'),
}),
    data=string_lazy(
"""
```
#!javascript

{
    "REMOTE_ADDR": "127.0.0.1" || null,
    "REMOTE_HOST": "example.org" || null,
    "default language": "en",
    "request language": "ru",
    "is_authenticated": true,
    "types": {
        "string": "%s",
        "datetime": "2014-01-01T00:00:00.000Z",
        "date": "2014-01-01",
        "time": "00:00:00.000",
        "decimal": "12345678.90",
        "float": 12345678.9,
        "integer": 1234567890,
    },
    "settings": {
        "QUICKAPI_DEFINED_METHODS": {
            "quickapi.test": "quickapi.views.test"
        }, 
        "QUICKAPI_INDENT": 2, 
        "QUICKAPI_DECIMAL_LOCALE": false, 
        "QUICKAPI_ONLY_AUTHORIZED_USERS": false, 
        "QUICKAPI_DEBUG": false, 
        "QUICKAPI_SWITCH_LANGUAGE_AUTO": true, 
        "QUICKAPI_SWITCH_LANGUAGE": true,
        "QUICKAPI_ENSURE_ASCII": false,
        "QUICKAPI_PYGMENTS_STYLE": "default",
        "QUICKAPI_VERSIONS": {/*%s*/}
    }
}
```
""", (_('String in your localization'), _('versions of components'))),
    footer=_('*In debug mode shows the settings. Here are the default.* <a href="./?method=quickapi.test">Click for test</a>.')
)


METHODS = get_methods() # store default methods from settings


@csrf_exempt
def index(request, methods=METHODS):
    """
    Распределяет запросы либо отдавая страницу документации, либо
    вызывая метод.

    Структура запроса для выполнения метода:

        {
            'method': 'Имя вызываемого метода',
            'kwargs': { Словарь параметров },
            # Необязательные ключи могут браться из сессии, либо из
            # заголовков запроса (например HTTP Basic Authorization).
            # Список необязательные ключей:
            'username': 'имя пользователя',
            'password': 'пароль пользователя',
        }

    Параметр "methods" может использоваться сторонними приложениями
    для организации определённых наборов методов API.

    По-умолчанию словарь методов может определяться в переменной
    `settings.QUICKAPI_DEFINED_METHODS` главного проекта.

    """

    switch_language(request)

    if is_callable(request):
        return run(request, methods)

    ctx = {}
    ctx['api_url'] = clean_uri(request)
    ctx['methods'] = methods.values()
    ctx['test_method_doc'] = test.__doc__ if not 'quickapi.test' in methods else None

    return render(request, 'quickapi/index.html', ctx)


# short name
api = index


def run(request, methods):
    """
    Авторизует пользователя, если он не авторизован и запускает методы.

    Параметры авторизации запрещается передавать в GET-запросе, для
    таких случаев их необходимо передавать в заголовке запроса,
    специально предназначенного для Basic-авторизации.

    """

    is_authenticated = request.user.is_authenticated()

    # Нарушителей правил передачи параметров авторизации
    # направляем на страницу документации
    if warning_auth_in_get(request):
        url = clean_uri(request)+'#requests-auth'
        msg = _('You made a dangerous request. Please, read the docs: %s') % url
        return HttpResponseBadRequest(content=force_text(msg))

    if request.method == 'GET':
        REQUEST = request.GET
    else:
        REQUEST = request.POST

    if 'method' in REQUEST:
        method = REQUEST.get('method')

        kwargs = clean_kwargs(request, REQUEST)

        if not is_authenticated:
            is_authenticated = login_from_request(request, REQUEST)

    elif 'jsonData' in REQUEST:
        try:
            data   = json.loads(REQUEST.get('jsonData'))
            method = data.get('method')
            kwargs = data.get('kwargs', clean_kwargs(request, data))
        except Exception as e:
            return HttpResponseBadRequest(content='%s\n%s' % (force_text(MESSAGES[400]), force_text(e)))

        if not is_authenticated:
            is_authenticated = login_from_request(request, data)

    else:
        return HttpResponseBadRequest(content=force_text(MESSAGES[400]))

    if not is_authenticated:
        if conf.QUICKAPI_ONLY_AUTHORIZED_USERS and method != 'quickapi.test':
            meta = request.META
            ip = meta.get("HTTP_X_REAL_IP", meta.get("REMOTE_ADDR", None))
            logger.info('The attempt unauthorized access to method `%s` on %s from IP: %s.',
                        method, request.path, ip)
            return HttpResponseBadRequest(status=401, content=force_text(MESSAGES[401]))

    if conf.QUICKAPI_DEBUG:
        logger.debug('Run method `%s` on %s', method, request.path)

    if method in methods:
        real_method = methods[method]['method']
    elif method == 'quickapi.test':
        real_method = test
    else:
        return HttpResponseBadRequest(status=405, content=force_text(MESSAGES[405]))

    return real_method(request, **kwargs)


