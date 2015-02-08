# -*- coding: utf-8 -*-
#
#  quickapi/utils/lang.py
#  
#  Copyright 2012 Grigoriy Kramarenko <root@rosix.ru>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
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

    if code:
        new_language = code
    elif 'language' in request.POST:
        new_language = request.POST.get('language')
    elif QUICKAPI_SWITCH_LANGUAGE_AUTO and hasattr(request, 'LANGUAGE_CODE'):
        new_language = request.LANGUAGE_CODE

    if new_language:
        try:
            translation.activate(new_language)
        except:
            translation.activate(old_language)
            new_language = None

    return old_language, new_language

