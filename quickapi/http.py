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
from django.conf import settings
from django.http import HttpResponse
from django.utils.functional import Promise
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import is_aware

from quickapi.conf import QUICKAPI_INDENT

import datetime, decimal, json as jsonlib

MESSAGES = {
#1xx
    100: _('Continue'),
    101: _('Switching Protocols'),
    102: _('Processing'),
#2xx
    200: _('OK'),
    201: _('Created'),
    202: _('Accepted'),
    203: _('Non-Authoritative Information'),
    204: _('No Content'),
    205: _('Reset Content'),
    206: _('Partial Content'),
    207: _('Multi-Status'),
    226: _('IM Used'),
#3xx
    300: _('Multiple Choices'),
    301: _('Moved Permanently'),
    302: _('Found'),
    303: _('See Other'),
    304: _('Not Modified'),
    305: _('Use Proxy'),
    307: _('Temporary Redirect'),
#4xx
    400: _('Bad Request'),
    401: _('Unauthorized'),
    402: _('Payment Required'),
    403: _('Forbidden'),
    404: _('Not Found'),
    405: _('Method Not Allowed'),
    406: _('Not Acceptable'),
    407: _('Proxy Authentication Required'),
    408: _('Request Timeout'),
    409: _('Conflict'),
    410: _('Gone'),
    411: _('Length Required'),
    412: _('Precondition Failed'),
    413: _('Request Entity Too Large'),
    414: _('Request-URI Too Large'),
    415: _('Unsupported Media Type'),
    416: _('Requested Range Not Satisfiable'),
    417: _('Expectation Failed'),
    422: _('Unprocessable Entity'),
    423: _('Locked'),
    424: _('Failed Dependency'),
    425: _('Unordered Collection'),
    426: _('Upgrade Required'),
    449: _('Retry With'),
    456: _('Unrecoverable Error'),
# 5xx
    500: _('Internal Server Error'),
    501: _('Not Implemented'),
    502: _('Bad Gateway'),
    503: _('Service Unavailable'),
    504: _('Gateway Timeout'),
    505: _('HTTP Version Not Supported'),
    506: _('Variant Also Negotiates'),
    507: _('Insufficient Storage'),
    508: _('Loop Detected'),
    509: _('Bandwidth Limit Exceeded'),
    510: _('Not Extended'),
}

class JSONEncoder(jsonlib.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time, decimal
    types and Lazy objects.
    """
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, decimal.Decimal):
            return float(o)
        elif isinstance(o, Promise):
            return unicode(o)
        else:
            return super(JSONEncoder, self).default(o)

DjangoJSONEncoder = JSONEncoder

def _get_json_response(ctx={}):
    result = jsonlib.dumps(ctx, ensure_ascii=True, 
                            cls=DjangoJSONEncoder,
                            indent=QUICKAPI_INDENT,
                        )
    try:
        result = result.encode(settings.DEFAULT_CHARSET)
    except:
        pass
    content_type = "%s; charset=%s" % ("application/json",
                    settings.DEFAULT_CHARSET)
    response = HttpResponse(content_type=content_type)
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
        dic['message'] = MESSAGES.get(dic['status'], _('Undefined message'))
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
