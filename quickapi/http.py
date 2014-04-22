# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.encoding import smart_text
from django.utils import six
from django.conf import settings
from django.http import HttpResponse
from django.utils.functional import Promise
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import is_aware
from django.utils.formats import number_format

from quickapi.conf import (QUICKAPI_INDENT, QUICKAPI_DECIMAL_LOCALE,
    QUICKAPI_ENSURE_ASCII)

import datetime, decimal, zlib, json as jsonlib

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
            if QUICKAPI_DECIMAL_LOCALE:
                return number_format(o, use_l10n=True, force_grouping=True)
            else:
                return str(o)
        elif isinstance(o, Promise):
            return six.text_type(o)
        else:
            return super(JSONEncoder, self).default(o)

DjangoJSONEncoder = JSONEncoder

def tojson(ctx, indent=None):
    result = jsonlib.dumps(ctx, ensure_ascii=QUICKAPI_ENSURE_ASCII, cls=JSONEncoder, indent=indent)
    result = result.encode(settings.DEFAULT_CHARSET)
    return result

def get_json_response(ctx=None):
    result = tojson(ctx, indent=QUICKAPI_INDENT)
    content_type = "%s; charset=%s" % ("application/json", settings.DEFAULT_CHARSET)
    response = HttpResponse(content_type=content_type)
    if len(result)>512:
        response['Content-encoding'] = 'deflate'
        result = zlib.compress(result)
    response.write(result)
    return response

# compatibility older
_get_json_response = get_json_response

def check_status(dic):
    if not isinstance(dic['status'], int):
        dic['status'] = int(dic['status'])
    return dic

def check_message(dic):
    if dic['message'] is None:
        dic['message'] = MESSAGES.get(dic['status'], _('Undefined message'))
    return dic

def JSONResponse(data=None, message=None, status=200, **kwargs):
    dic = {
        'status': status,
        'message': message,
        'data': data,
    }
    dic.update(kwargs)
    dic = check_message(check_status(dic))
    return get_json_response(dic)

def JSONRedirect(location='/', message=None, status=301, **kwargs):
    dic = {
        'status': status,
        'message': message,
        'data': { 'Location': location },
    }
    dic.update(kwargs)
    dic = check_message(check_status(dic))
    return get_json_response(dic)
