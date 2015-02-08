# -*- coding: utf-8 -*-
#
#  quickapi/views.py
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
import logging
import traceback
import decimal
import json

from django.utils import six
from django.utils.encoding import force_text
from django.contrib.auth import authenticate, login
from django.core.mail import mail_admins
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.termcolors import colorize
from django.utils.translation import ugettext_lazy as _

from quickapi.http import JSONResponse, JSONRedirect, MESSAGES
from quickapi.conf import (settings,
    QUICKAPI_DEFINED_METHODS,
    QUICKAPI_ONLY_AUTHORIZED_USERS,
    QUICKAPI_INDENT,
    QUICKAPI_DEBUG,
    QUICKAPI_SWITCH_LANGUAGE,
    QUICKAPI_SWITCH_LANGUAGE_AUTO,
    QUICKAPI_DECIMAL_LOCALE,
    QUICKAPI_ENSURE_ASCII)
from quickapi.utils.method import get_methods
from quickapi.utils.doc import apidoc_lazy, string_lazy
from quickapi.utils.lang import switch_language
from quickapi.utils.parsers import parse_auth, clean_kwargs


@csrf_exempt
def test(request, code=200, redirect='/'):
    """
    Test response
    """

    if code in (301, 302):
        return JSONRedirect(location=redirect, status=code,
                message=_('Test response. Redirect to %s.') % redirect)
    elif code == 400:
        return JSONResponse(status=400, message=_('Test response. Error 400.'))
    elif code == 500:
        return JSONResponse(status=500, message=_('Test response. Error 500.'))

    now = timezone.now()

    data = {
        'REMOTE_ADDR': request.META.get("HTTP_X_REAL_IP", request.META.get("REMOTE_ADDR", None)),
        'REMOTE_HOST': request.META.get("REMOTE_HOST", None),
        'default language': settings.LANGUAGE_CODE,
        'request language': request.POST.get('language', getattr(request, 'LANGUAGE_CODE', None)),
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
            'QUICKAPI_DEFINED_METHODS': QUICKAPI_DEFINED_METHODS,
            'QUICKAPI_ONLY_AUTHORIZED_USERS': QUICKAPI_ONLY_AUTHORIZED_USERS,
            'QUICKAPI_INDENT': QUICKAPI_INDENT,
            'QUICKAPI_DEBUG': QUICKAPI_DEBUG,
            'QUICKAPI_SWITCH_LANGUAGE': QUICKAPI_SWITCH_LANGUAGE,
            'QUICKAPI_SWITCH_LANGUAGE_AUTO': QUICKAPI_SWITCH_LANGUAGE_AUTO,
            'QUICKAPI_DECIMAL_LOCALE': QUICKAPI_DECIMAL_LOCALE,
            'QUICKAPI_ENSURE_ASCII': QUICKAPI_ENSURE_ASCII,
        }
    return JSONResponse(data=data)

test.__doc__ = apidoc_lazy(
    header=_("""*Test response*"""),
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
        "QUICKAPI_ENSURE_ASCII": false
    }
}
```
""", _('String in your localization')),
    footer=_('*In debug mode shows the settings. Here are the default.*')
)


METHODS = get_methods() # store default methods from settings


@csrf_exempt
def index(request, methods=METHODS):
    """ Распределяет запросы.
        Структура запроса = {
            'method': u'Имя вызываемого метода',
            'kwargs': { Словарь параметров },
            # Необязательные ключи могут браться из сессии, либо из
            # заголовков запроса (например HTTP Basic Authorization).
            # Список необязательные ключей:
            'user': u'имя пользователя',
            'pass': u'пароль пользователя',
        }
        Параметр "methods" может использоваться сторонними приложениями
        для организации определённых наборов методов API.

        По-умолчанию словарь методов может определяться в переменной
        settings.QUICKAPI_DEFINED_METHODS главного проекта.
    """

    switch_language(request)

    # When accessed from third-party programs, such as Python,
    # request.is_ajax() is equal to false
    if request.is_ajax() or request.method == 'POST':
        try:
            return run(request, methods)
        except Exception as e:
            # unexpected error
            if QUICKAPI_DEBUG:
                print(colorize(force_text(e), fg='red'))
            return JSONResponse(status=500, message=force_text(e))

    # Vars for docs
    ctx = {}
    url = request.build_absolute_uri().split(request.path)[0] + request.path
    ctx['api_url'] = url
    ctx['methods'] = methods.values()
    ctx['test_method_doc'] = test.__doc__ if not 'quickapi.test' in methods else None

    return render_to_response('quickapi/index.html', ctx,
                            context_instance=RequestContext(request,))


# short name
api = index


def run(request, methods):
    """ Авторизует пользователя, если он не авторизован и запускает методы """

    is_authenticate = request.user.is_authenticated()


    if 'method' in request.POST:
        method = request.POST.get('method', 'quickapi.test')
        kwargs = clean_kwargs(request, request.POST)
        if not is_authenticate:
            username, password = parse_auth(request, request.POST)
    elif request.method == 'POST':
        try:
            data   = json.loads(request.POST.get('jsonData', list(request.POST.keys())[0]))
            method = data.get('method', 'quickapi.test')
            kwargs = data.get('kwargs', clean_kwargs(request, data))

        except Exception as e:
            
            logger = logging.getLogger('quickapi.views.run')

            if QUICKAPI_DEBUG:
                print(colorize('%s: %s' % (logger.name, force_text(e)), fg='red'))

            logger.error(traceback.format_exc())

            return JSONResponse(status=400, message=force_text(e))
        else:
            if not is_authenticate:
                username, password = parse_auth(request, data)
    else:
        return JSONResponse(status=400)

    if not is_authenticate:
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(request, user)
            is_authenticate = True

        elif QUICKAPI_ONLY_AUTHORIZED_USERS and method != 'quickapi.test':

            return JSONResponse(status=401)


    logger = logging.getLogger('quickapi.method.%s' % method)

    if QUICKAPI_DEBUG:
        print(colorize(logger.name, fg='blue'))


    if method in methods:
        try:
            real_method = methods[method]['method']
        except Exception as e:
            if QUICKAPI_DEBUG:
                print(colorize('%s: %s' % (logger.name, force_text(e)), fg='red'))

            logger.error(traceback.format_exc())

            return JSONResponse(status=500, message=force_text(e))

    elif method == 'quickapi.test':
        real_method = test
    else:
        e = _('Method `%s` does not exist') % method

        if QUICKAPI_DEBUG:
            print(colorize('%s: %s' % (logger.name, force_text(e)), fg='red'))

        logger.warning(force_text(e))

        return JSONResponse(status=405, message=force_text(e))

    try:
        return real_method(request, **kwargs)
    except TypeError as e:
        if QUICKAPI_DEBUG:
            print(colorize('%s: %s' % (logger.name, force_text(e)), fg='red'))

        logger.warning(traceback.format_exc())

        return JSONResponse(status=400, message=force_text(e))

    except Exception as e:
        if QUICKAPI_DEBUG:
            print(colorize('%s: %s' % (logger.name, force_text(e)), fg='red'))

        logger.error(traceback.format_exc())

        return JSONResponse(status=500, message=force_text(e))

