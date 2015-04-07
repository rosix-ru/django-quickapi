# -*- coding: utf-8 -*-
#
#   Copyright 2012-2015 Grigoriy Kramarenko <root@rosix.ru>
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

from django.utils import translation

from quickapi.conf import (settings, QUICKAPI_SWITCH_LANGUAGE,
    QUICKAPI_SWITCH_LANGUAGE_AUTO)


def switch_language(request, code=None):
    """
    Переключает язык для приложения, если такое переключение не
    запрещено в настройках.
    """

    if not QUICKAPI_SWITCH_LANGUAGE and not code:
        # Disabled switching for quickapi only
        return settings.LANGUAGE_CODE, None

    old_language = translation.get_language()
    new_language = None

    if request.method == 'GET':
        REQUEST = request.GET
    else:
        REQUEST = request.POST

    if code:
        new_language = code
    elif 'language' in REQUEST:
        new_language = REQUEST.get('language')
    elif QUICKAPI_SWITCH_LANGUAGE_AUTO and hasattr(request, 'LANGUAGE_CODE'):
        new_language = request.LANGUAGE_CODE

    if new_language:
        try:
            translation.activate(new_language)
        except:
            translation.activate(old_language)
            new_language = None

    return old_language, new_language

