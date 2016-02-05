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
from datetime import datetime, date, time
from decimal import Decimal
from types import GeneratorType
from uuid import UUID

from django.utils.encoding import force_text
from django.utils.functional import Promise
from django.utils.timezone import is_aware
from django.utils.formats import number_format

from quickapi.conf import (QUICKAPI_INDENT, QUICKAPI_ENSURE_ASCII,
                           QUICKAPI_DECIMAL_LOCALE)


class JSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time, decimal
    types, generators and Lazy objects.
    Almost like in Django, but with additions.
    """
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, Decimal):
            if QUICKAPI_DECIMAL_LOCALE:
                return number_format(o, use_l10n=True, force_grouping=True)
            else:
                return force_text(o)
        elif isinstance(o, (Promise, Exception, UUID)):
            return force_text(o)
        elif isinstance(o, GeneratorType):
            return list(o)
        else:
            return super(JSONEncoder, self).default(o)


def tojson(ctx, indent=QUICKAPI_INDENT):
    """
    Convert context to JSON.
    """
    return json.dumps(ctx, ensure_ascii=QUICKAPI_ENSURE_ASCII,
                      cls=JSONEncoder, indent=indent)


