# -*- coding: utf-8 -*-
"""
###############################################################################
# Copyright 2012 Grigoriy Kramarenko.
###############################################################################
# This file is part of QUICKAPI.
#
#    QUICKAPI is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    QUICKAPI is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with QUICKAPI.  If not, see <http://www.gnu.org/licenses/>.
#
# Этот файл — часть QUICKAPI.
#
#   QUICKAPI - свободная программа: вы можете перераспространять ее и/или
#   изменять ее на условиях Стандартной общественной лицензии GNU в том виде,
#   в каком она была опубликована Фондом свободного программного обеспечения;
#   либо версии 3 лицензии, либо (по вашему выбору) любой более поздней
#   версии.
#
#   QUICKAPI распространяется в надежде, что она будет полезной,
#   но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА
#   или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной
#   общественной лицензии GNU.
#
#   Вы должны были получить копию Стандартной общественной лицензии GNU
#   вместе с этой программой. Если это не так, см.
#   <http://www.gnu.org/licenses/>.
###############################################################################
"""
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.models import Site
from django.conf import settings

from http import JSONResponse, MESSAGES
from conf import QUICKAPI_DEFINED_METHODS

@csrf_exempt
def test(request):
    """ Тестовый ответ """
    data = {
        'integer': 9999,
        'float': 9999.999,
        'boolean': True,
        'string': 'String',
        'list': [9999, True, 'String'],
        'dict': {'a': 1, 'b': 2, 'c': 3}
    }
    return JSONResponse(data=data)

METHODS = {}
for key,val in QUICKAPI_DEFINED_METHODS.items():
    try:
        method = __import__(val, fromlist=[''])
    except ImportError:
        try:
            L = val.split('.')
            _method = L[-1]
            _module = '.'.join(L[:-1])
            module = __import__(_module, fromlist=[''])
            method = getattr(module, _method)
        except ImportError as e:
            print e
            method = None
    if method:
        METHODS[key] = { 'method': method, 'doc': method.__doc__, 'name': key }

@csrf_exempt
def api(request):
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
    """
    if request.is_ajax() or request.POST:
        try:
            return run(request)
        except Exception as e:
            print e
            return JSONResponse(status=500, message=unicode(e))
    # Vars for docs
    ctx = {}
    ctx['site'] = Site.objects.get(id=settings.SITE_ID)
    ctx['methods'] = METHODS.values()
    return render_to_response('quickapi/index.html', ctx,
                            context_instance=RequestContext(request,))

def run(request):
    """ Авторизует пользователя, если он не авторизован и запускает методы """

    is_authenticate = not request.user.is_anonymous()

    def _auth(post):
        if request.META.has_key('HTTP_AUTHORIZATION'):
            key = request.META['HTTP_AUTHORIZATION']
        elif request.META.has_key('HTTP_X_AUTHORIZATION'):
            key = request.META['HTTP_X_AUTHORIZATION']
        else:
            return post.get('username', None), post.get('password', None)
        if key.lower().count('basic'):
            return key[6:].decode('base64').split(':')
        else:
            return None, None

    if 'method' in request.POST:
        method = request.POST.get('method', 'quickapi.test')
        kwargs = {}
        for key in request.POST.keys():
            if '[]' in key:
                kwargs[key.replace('[]','')] = request.POST.getlist(key)
            elif key not in ('method','username','password'):
                kwargs[key] = request.POST.get(key)
        if not is_authenticate:
            username, password = _auth(request.POST)
    elif request.method == 'POST':
        try:
            json = simplejson.loads(request.POST.get('jsonData', request.POST.keys()[0]))
            method = json.get('method', 'quickapi.test')
            kwargs = json.get('kwargs', {})
        except Exception as e:
            print e
            return JSONResponse(status=400, message=unicode(e))
        else:
            if not is_authenticate:
                username, password = _auth(json)
    else:
        return JSONResponse(status=400, message=MESSAGES[400])

    if not is_authenticate:
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
        else:
            return JSONResponse(status=401, message=MESSAGES[401])

    try:
        real_method = METHODS[method]['method']
    except Exception as e:
        if settings.DEBUG:
            msg = unicode(e)
        else:
            msg = MESSAGES[405]
        print e
        return JSONResponse(status=405, message=msg)
    try:
        return real_method(request, **kwargs)
    except Exception as e:
        if settings.DEBUG:
            msg = unicode(e)
        else:
            msg = MESSAGES[415]
        print e
        return JSONResponse(status=415, message=msg)
