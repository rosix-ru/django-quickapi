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
from django.contrib.auth import authenticate, login
from django.core.mail import mail_admins
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.termcolors import colorize
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from quickapi.http import JSONResponse, MESSAGES
from quickapi.conf import (settings, QUICKAPI_DEFINED_METHODS,
    QUICKAPI_ONLY_AUTHORIZED_USERS, QUICKAPI_DEBUG, DEBUG, SITE_ID,
    QUICKAPI_SWITCH_LANGUAGE, QUICKAPI_SWITCH_LANGUAGE_AUTO)

import traceback, json as jsonlib, decimal

if 'django.contrib.sites' in settings.INSTALLED_APPS:
    from django.contrib.sites.models import Site
    site = Site.objects.get(id=SITE_ID)
else:
    site = None

def switch_language(request, code=None):
    """
    Переключает язык для приложения, если такое переключение не
    запрещено в настройках.
    """
    old_language = translation.get_language()

    if not QUICKAPI_SWITCH_LANGUAGE and not code:
        # Disabled switching for quickapi only
        return settings.LANGUAGE_CODE, old_language

    new_language = None

    if code:
        new_language = code
    elif 'language' in request.POST:
        new_language = request.POST.get('language')
    elif QUICKAPI_SWITCH_LANGUAGE_AUTO and hasattr(request, 'LANGUAGE_CODE'):
        new_language = request.LANGUAGE_CODE

    if new_language:
        try:
            new_language = translation.activate(new_language)
        except:
            translation.activate(old_language)
            new_language = None

    return old_language, new_language

@csrf_exempt
def test(request):
    """
    Test response
    """

    default_language, request_language = switch_language(request)

    data = {
        'REMOTE_ADDR': request.META.get("HTTP_X_REAL_IP", request.META.get("REMOTE_ADDR", None)),
        'REMOTE_HOST': request.META.get("REMOTE_HOST", None),
        'default language': default_language,
        'request language': request_language,
        'string': _('String in your localization'),
        'datetime': timezone.now(),
        'is_authenticated': request.user.is_authenticated(),
    }
    return JSONResponse(data=data)

test.__doc__ = _("""
*Test response*

#### Request parameters
Nothing

#### Returned object
`{
    'REMOTE_ADDR': '127.0.0.1' || null,
    'REMOTE_HOST': 'example.org' || null,
    'default language': 'en',
    'request language': 'ru',
    'string': 'String in your localization',
    'datetime': '2013-01-01T00:00:00.000Z',
    'is_authenticated': true,
}`
""")

class Collection(object):
    """
    Класс, реализующий отсортированный словарь методов
    """

    def __init__(self):
        self._COLLECTION = {}
        self._CHAIN      = []

    def __bool__(self):
        return bool(self._CHAIN)

    def __len__(self):
        return len(self._CHAIN)

    def __setitem__(self, name, value):
        self._COLLECTION[name] = value
        if not name in self._CHAIN:
            self._CHAIN.append(name)

    def __setattr__(self, name, value):
        if name in ('_COLLECTION', '_CHAIN'):
            return super(Collection, self).__setattr__(name, value)
        self.__setitem__(name, value)

    def __getitem__(self, name):
        return self._COLLECTION[name]

    def __contains__(self, name):
        return name in self._COLLECTION

    def __getattr__(self, name):
        if name in ('_COLLECTION', '_CHAIN'):
            return super(Collection, self).__getattr__(name, value)
        return self.__getitem__(name)

    def __delitem__(self, name):
        del self._COLLECTION[name]
        del self._CHAIN[self._CHAIN.index(name)]

    def __delattr__(self, name):
        if name in ('_COLLECTION', '_CHAIN'):
            raise AttributeError('Is internal attribute')
        self.__delitem__(name)

    def items(self):
        return [(name, self._COLLECTION[name]) for name in self._CHAIN]

    def keys(self):
        return self._CHAIN

    def values(self):
        return [self._COLLECTION[name] for name in self._CHAIN]

    def sort(self):
        self._CHAIN.sort()

def get_methods(list_or_dict=QUICKAPI_DEFINED_METHODS, sort=False):
    """ Преобразует словарь или список заданных строками методов,
        реальными объектами функций.
        Форматы list_or_dict:
        (('',''),('',''))
        либо
        [['',''],['','']]
        либо
        {'':'', '':''}
    """
    collection = Collection()

    if isinstance(list_or_dict, (list, tuple)):
        seq = list_or_dict
    elif isinstance(list_or_dict, dict):
        sort = True
        seq = list_or_dict.items()
    else:
        raise ValueError('Parameter must be sequence or dictionary')
    for key,val in seq:
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
                if QUICKAPI_DEBUG:
                    print colorize(unicode(e), fg='red')
                else:
                    print e
                method = None
        if method:
            collection[key] = {
                'method': method,
                'doc':    method.__doc__,
                'name':   key,
            }

    if sort:
        collection.sort()

    return collection

METHODS = get_methods()

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

    if QUICKAPI_DEBUG:
        p = '\nQUICKAPI:'
        print colorize(p, fg='blue')
        p = '\trequest.is_ajax()\t== %s' % request.is_ajax()
        print colorize(p, fg='blue')

    if request.is_ajax() or request.method == 'POST':
        try:
            return run(request, methods)
        except Exception as e:
            if QUICKAPI_DEBUG:
                print colorize(unicode(e), fg='red')
            return JSONResponse(status=500, message=unicode(e))

    # Vars for docs
    ctx = {}
    ctx['site'] = site
    ctx['methods'] = methods.values()
    ctx['test_method_doc'] = test.__doc__ if not 'quickapi.test' in methods else None

    return render_to_response('quickapi/index.html', ctx,
                            context_instance=RequestContext(request,))

# Older
api = index

def run(request, methods):
    """ Авторизует пользователя, если он не авторизован и запускает методы """

    switch_language(request)

    is_authenticate = request.user.is_authenticated()
    if QUICKAPI_DEBUG:
        p = '\trun as user\t\t== %s' % request.user
        print colorize(p, fg='blue')

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

    def _get_kwargs(post):
        kwargs = {}
        for key in post.keys():
            if '[]' in key and post is request.POST:
                kwargs[key.replace('[]','')] = post.getlist(key)
            elif key not in ('method','username','password'):
                kwargs[key] = post.get(key)
        return kwargs

    if 'method' in request.POST:
        method = request.POST.get('method', 'quickapi.test')
        kwargs = _get_kwargs(request.POST)
        if not is_authenticate:
            username, password = _auth(request.POST)
    elif request.method == 'POST':
        try:
            json = jsonlib.loads(request.POST.get('jsonData', request.POST.keys()[0]))
            method = json.get('method', 'quickapi.test')
            kwargs = json.get('kwargs', _get_kwargs(json))
        except Exception as e:
            pe = '\t%s' % e
            ppost = '\trequest.POST\t\t== %s' % request.POST
            if QUICKAPI_DEBUG:
                print colorize(pe, fg='red')
                print colorize(ppost, fg='blue')
            else:
                print pe
                print ppost
            return JSONResponse(status=400, message=unicode(e))
        else:
            if not is_authenticate:
                username, password = _auth(json)
    else:
        return JSONResponse(status=400)

    if not is_authenticate:
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
        elif QUICKAPI_ONLY_AUTHORIZED_USERS and method != 'quickapi.test':
            return JSONResponse(status=401)

    if QUICKAPI_DEBUG:
        p = '\tlogin user\t\t== %s' % request.user
        print colorize(p, fg='blue')
        p = '\tmethod\t\t\t== %s' % method
        print colorize(p, fg='blue')

    if method in methods:
        try:
            real_method = methods[method]['method']
        except Exception as e:
            msg = traceback.format_exc(e)
            if DEBUG:
                print msg
            else:
                msg = MESSAGES[405]
            return JSONResponse(status=405, message=msg)
    elif method == 'quickapi.test':
        real_method = test
    else:
        msg = _('Method `%s` does not exist') % method
        if DEBUG:
            print msg
        return JSONResponse(status=405, message=msg)

    try:
        return real_method(request, **kwargs)
    except Exception as e:
        msg = traceback.format_exc(e)
        if DEBUG:
            print msg
        else:
            try:
                msg = msg.decode('utf-8')
            except:
                pass
            mail_admins(u'QuickAPI method error', msg +'\n\n'+ unicode(request))
        try:
            return JSONResponse(status=500, message=str(e).decode('utf-8'))
        except:
            try:
                return JSONResponse(status=500, message=unicode(e))
            except:
                pass
            return JSONResponse(status=500, message=MESSAGES[500])
