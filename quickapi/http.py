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

Структура ответа outdict = {
    'status': 200, # коды HTTP, имеющие смысл.
    'message': u'Строчное сообщение для пользователя',
    'data': <Сериализованный объект JSON>,
}

Пример outdict при возврате единичной настройки пользователя:
outdic = {
    'status': 200,
    'message': u'Количество объектов на одной странице',
    'data': 25,
}

Пример outdict с переадресацией:
outdic = {
    'status': 303,
    'message': u'Смотрите на другой странице',
    'data': { 'Location': '/other-page/', },
},
либо:
outdict = {
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
#1xx
    100: ugettext('Continue'),
    101: ugettext('Switching Protocols'),
    102: ugettext('Processing'),
#2xx
    200: ugettext('OK'),
    201: ugettext('Created'),
    202: ugettext('Accepted'),
    203: ugettext('Non-Authoritative Information'),
    204: ugettext('No Content'),
    205: ugettext('Reset Content'),
    206: ugettext('Partial Content'),
    207: ugettext('Multi-Status'),
    226: ugettext('IM Used'),
#3xx
    300: ugettext('Multiple Choices'),
    301: ugettext('Moved Permanently'),
    302: ugettext('Found'),
    303: ugettext('See Other'),
    304: ugettext('Not Modified'),
    305: ugettext('Use Proxy'),
    307: ugettext('Temporary Redirect'),
#4xx
    400: ugettext('Bad Request'),
    401: ugettext('Unauthorized'),
    402: ugettext('Payment Required'),
    403: ugettext('Forbidden'),
    404: ugettext('Not Found'),
    405: ugettext('Method Not Allowed'),
    406: ugettext('Not Acceptable'),
    407: ugettext('Proxy Authentication Required'),
    408: ugettext('Request Timeout'),
    409: ugettext('Conflict'),
    410: ugettext('Gone'),
    411: ugettext('Length Required'),
    412: ugettext('Precondition Failed'),
    413: ugettext('Request Entity Too Large'),
    414: ugettext('Request-URI Too Large'),
    415: ugettext('Unsupported Media Type'),
    416: ugettext('Requested Range Not Satisfiable'),
    417: ugettext('Expectation Failed'),
    422: ugettext('Unprocessable Entity'),
    423: ugettext('Locked'),
    424: ugettext('Failed Dependency'),
    425: ugettext('Unordered Collection'),
    426: ugettext('Upgrade Required'),
    449: ugettext('Retry With'),
    456: ugettext('Unrecoverable Error'),
# 5xx
    500: ugettext('Internal Server Error'),
    501: ugettext('Not Implemented'),
    502: ugettext('Bad Gateway'),
    503: ugettext('Service Unavailable'),
    504: ugettext('Gateway Timeout'),
    505: ugettext('HTTP Version Not Supported'),
    506: ugettext('Variant Also Negotiates'),
    507: ugettext('Insufficient Storage'),
    508: ugettext('Loop Detected'),
    509: ugettext('Bandwidth Limit Exceeded'),
    510: ugettext('Not Extended'),
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

def check_status(dic):
    if not isinstance(dic['status'], int):
        dic['status'] = int(dic['status'])
    return dic

def check_message(dic):
    if dic['message'] is None:
        dic['message'] = MESSAGES.get(dic['status'], ugettext('Undefined message'))
    return dic

def JSONResponse(data={}, message=None, status=200, **kwargs):
    dic = {
        'status': status,
        'message': message,
        'data': data,
    }
    dic.update(kwargs)
    dic = check_message(check_status(dic))
    return _get_json_response(dic)

def JSONRedirect(location='/', message=None, status=301, **kwargs):
    dic = {
        'status': status,
        'message': message,
        'data': { 'Location': location },
    }
    dic.update(kwargs)
    dic = check_message(check_status(dic))
    return _get_json_response(dic)
