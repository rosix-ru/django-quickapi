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

Структура запроса indic = {
    'method': u'Имя вызываемого метода',
    'kwargs': { Словарь параметров },
    # Необязательные ключи:
    'user': u'имя пользователя',
    'pass': u'пароль пользователя',
}
Структура ответа outdic = {
    'status': 200, # коды HTTP, имеющие смысл.
    'message': u'Строчное сообщение для пользователя',
    'data': <Сериализованный объект JSON>,
}

Пример outdic при возврате единичной настройки пользователя:
outdic = {
    'status': 200,
    'message': u'Количество объектов на одной странице',
    'data': 25,
}

Пример outdic с переадресацией:
outdic = {
    'status': 303,
    'message': u'Смотрите на другой странице',
    'data': { 'Location': '/other-page/', },
},
либо:
outdic = {
    'status': 401,
    'message': u'Пользователь не авторизован',
    'data': { 'Location': '/accounts/login/', },
}
"""
from django.utils.translation import ugettext
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson

MESSAGES = {
    200: ugettext('OK'),
    201: ugettext('Created'),
    202: ugettext('Accepted'),
    301: ugettext('Moved Permanently'),
    302: ugettext('Moved Temporarily'),
    400: ugettext('Bad Request'),
    401: ugettext('Unauthorized'),
    402: ugettext('Payment Required'),
    403: ugettext('Forbidden'),
    404: ugettext('Not Found'),
    405: ugettext('Method Not Allowed'),
    406: ugettext('Not Acceptable'),
    500: ugettext('Internal Server Error'),
}

def _get_json_response(ctx={}):
    result = simplejson.dumps(ctx, ensure_ascii=False, 
                            cls=DjangoJSONEncoder,
                            indent=4,
                        ).encode('utf-8', 'ignore')
    response = HttpResponse(mimetype="application/json",
        content_type="application/json")
    if len(result)>512:
        response['Content-encoding'] = 'deflate'
        result = result.encode('zlib')
    response.write(result)
    return response

def JSONResponse(**kwargs):
    dic = {
        'status': 200,
        'message': MESSAGES[200],
        'data': {},
    }
    dic.update(kwargs)
    return _get_json_response(dic)

def JSONRedirect(**kwargs):
    dic = {
        'status': 301,
        'message': MESSAGES[301],
        'data': { 'Location': '/' },
    }
    dic.update(kwargs)
    return _get_json_response(dic)
