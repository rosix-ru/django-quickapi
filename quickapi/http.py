# -*- coding: utf-8 -*-
#
#   Copyright 2012-2016 Grigoriy Kramarenko <root@rosix.ru>
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
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.cache import add_never_cache_headers

from quickapi.serializers import JSONEncoder, tojson


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
    208: _('Already Reported'),
    226: _('IM Used'),
#3xx
    300: _('Multiple Choices'),
    301: _('Moved Permanently'),
    302: _('Found'),
    303: _('See Other'),
    304: _('Not Modified'),
    305: _('Use Proxy'),
    307: _('Temporary Redirect'),
    308: _('Permanent Redirect'),
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
    418: _("I'm A Teapot"),
    422: _('Unprocessable Entity'),
    423: _('Locked'),
    424: _('Failed Dependency'),
    425: _('Unordered Collection'),
    426: _('Upgrade Required'),
    428: _('Precondition Required'),
    429: _('Too Many Requests'),
    431: _('Request Header Fields Too Large'),
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
    511: _('Network Authentication Required'),
}


def get_json_response(ctx=None, anticache=True):
    """
    Building JSON response.
    """
    result = tojson(ctx).encode(settings.DEFAULT_CHARSET)
    content_type = "application/json; charset=%s" % settings.DEFAULT_CHARSET
    response = HttpResponse(content_type=content_type)
    if anticache:
        add_never_cache_headers(response)
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


def JSONResponse(data=None, message=None, status=200, **kwargs):
    """
    Checks a context and returns full JSON response
    """
    dic = {
        'status': status,
        'message': message,
        'data': data,
    }
    dic.update(kwargs)
    dic = check_message(check_status(dic))
    return get_json_response(dic)


def JSONRedirect(location='/', message=None, status=302, **kwargs):
    """
    Redirect to page for this API.
    """
    dic = {
        'status': status,
        'message': message,
        'data': { 'Location': location },
    }
    dic.update(kwargs)
    dic = check_message(check_status(dic))
    return get_json_response(dic)

