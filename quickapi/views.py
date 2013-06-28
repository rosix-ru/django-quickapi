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
import json as jsonlib
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.models import Site
from django.utils.termcolors import colorize
from django.core.mail import mail_admins
import traceback

try:
    # Проверка установленного в системе markdown.
    from markdown import markdown as _markdown
except:
    markdown = lambda x: x
    BIT = '<br>'
else:
    markdown = lambda x: _markdown(x)
    BIT = '\n'

from http import JSONResponse, MESSAGES
from conf import QUICKAPI_DEFINED_METHODS, QUICKAPI_ONLY_AUTHORIZED_USERS,\
                 QUICKAPI_DEBUG, DEBUG, SITE_ID

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

def drop_space(doc):
    """ Удаление начальных и конечных пробелов в документации.
        Обратное слияние строк в текст зависит от наличия markdown
        в системе.
        
        Выравнивает весь код по первой его строке.
    """
    L = []
    cut = 0
    for s in doc.split('\n'):
        # Если начинается код
        if s.strip(' ').startswith('`'):
            cut = len(s[:s.find('`')]) # только выставляем обрезку
        # Если заканчивается код
        if s.strip().endswith('`'):
            L.append(s[cut:])          # то записываем,
            cut = 0                    # сбрасываем обрезку
            continue                   # и прерываем цикл
        # Теперь записываем
        if cut:
            L.append(s[cut:])          # с обрезкой
        else:
            L.append(s.strip(' '))     # или полностью очищенную строку
    return BIT.join(L)

def get_methods(dic=QUICKAPI_DEFINED_METHODS):
    """ Преобразует словарь заданных строками методов, реальными
        объектами функций.
    """
    methods = {}
    for key,val in dic.items():
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
                print colorize(unicode(e), fg='red')
                method = None
        if method:
            text = drop_space(method.__doc__)
            try:
                text = markdown(text.decode('utf-8'))
            except UnicodeDecodeError:
                try:
                    text = markdown(text)
                except:
                    pass
            methods[key] = {'method': method, 'doc': text, 'name': key}

    return methods

METHODS = get_methods()

@csrf_exempt
def index(request, dict_methods=None):
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
        Параметр "dict_methods" может использоваться сторонними приложениями
        для организации определённых наборов методов API.
        По-умолчанию словарь методов определяется в переменной
        settings.QUICKAPI_DEFINED_METHODS главного проекта.
    """
    if QUICKAPI_DEBUG:
        p = '\nQUICKAPI:'
        print colorize(p, fg='blue')
        p = '\trequest.is_ajax()\t== %s' % request.is_ajax()
        print colorize(p, fg='blue')

    if dict_methods is None:
        methods = METHODS
    else:
        methods = get_methods(dict_methods)

    if request.is_ajax() or request.method == 'POST':
        try:
            return run(request, methods)
        except Exception as e:
            if QUICKAPI_DEBUG:
                print colorize(unicode(e), fg='red')
            return JSONResponse(status=500, message=unicode(e))

    # Vars for docs
    ctx = {}
    ctx['site'] = Site.objects.get(id=SITE_ID)
    ctx['methods'] = methods.values()
    return render_to_response('quickapi/index.html', ctx,
                            context_instance=RequestContext(request,))

# Older
api = index

def run(request, methods):
    """ Авторизует пользователя, если он не авторизован и запускает методы """

    is_authenticate = not request.user.is_anonymous()
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
        elif QUICKAPI_ONLY_AUTHORIZED_USERS:
            return JSONResponse(status=401)

    if QUICKAPI_DEBUG:
        p = '\tlogin user\t\t== %s' % request.user
        print colorize(p, fg='blue')

    try:
        real_method = methods[method]['method']
    except Exception as e:
        msg = traceback.format_exc(e)
        if DEBUG:
            print msg
        else:
            msg = MESSAGES[405]
        return JSONResponse(status=405, message=msg)
    try:
        return real_method(request, **kwargs)
    except Exception as e:
        msg = traceback.format_exc(e)
        if DEBUG:
            print msg
        else:
            mail_admins('QuickAPI method error', msg +'\n\n'+ unicode(request))
            msg = MESSAGES[500]
        return JSONResponse(status=500, message=msg)
