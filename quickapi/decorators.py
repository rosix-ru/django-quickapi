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

import warnings
from functools import wraps

from django.utils.encoding import force_text
from django.utils.translation import ugettext as _
from django.http import HttpResponseBadRequest, HttpResponseServerError

from .http import JSONResponse, JSONRedirect, MESSAGES
from .utils.requests import is_callable, login_from_request


def auth_required(function=None, login_url=None):
    """
    Декоратор для методов QuickAPI, доступ к которым должны иметь 
    только авторизованные пользователи.
    """

    def decorator(view_func):

        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            u = request.user

            if u.is_active and u.is_authenticated() or login_from_request(request):
                return view_func(request, *args, **kwargs)

            if login_url:
                return HttpRedirect(login_url)
            return HttpResponseBadRequest(status=401, content=force_text(MESSAGES[401]))

        return _wrapped_view

    if function:
        return decorator(function)

    return decorator


def login_required(function=None, json_only=False, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """

    warnings.warn("QuickAPI decorator `login_required` is deprecated \
    and will be removed in QuickAPI 3.5. Use new `auth_required` decorator.")

    def decorator(view_func):

        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            u = request.user

            if u.is_active and u.is_authenticated():
                return view_func(request, *args, **kwargs)

            if json_only or request.is_ajax():
                if login_url:
                    return JSONRedirect(login_url)
                return JSONResponse(status=401)
            elif login_url:
                return HttpRedirect(login_url)
            else:
                return HttpResponseBadRequest(status=401, content=force_text(MESSAGES[401]))

        return _wrapped_view

    if function:
        return decorator(function)

    return decorator


def api_required(function=None, ajax_post=True, ajax_get=False,
    not_ajax_post=True, not_ajax_get=False):
    """
    Decorator for views that only work with API.
    By default GET requests denied.
    """

    def decorator(view_func):

        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not True in (ajax_post, ajax_get, not_ajax_post, not_ajax_get):
                return HttpResponseServerError(_('This method incorrectly configured.'))

            if request.method == 'POST':
                if not True in (ajax_post, not_ajax_post):
                    return HttpResponseBadRequest(_('This method not responsible on %s request.') % 'POST')

                elif request.is_ajax():
                    if not ajax_post:
                        return HttpResponseBadRequest(_('This method works without AJAX.'))
                
                elif not not_ajax_post:
                    return HttpResponseBadRequest(_('This method works with AJAX only.'))

            elif request.method == 'GET':
                if not True in (ajax_get, not_ajax_get):
                    return HttpResponseBadRequest(_('This method not responsible on %s request.') % 'GET')

                elif request.is_ajax():
                    if not ajax_get:
                        return HttpResponseBadRequest(_('This method works without AJAX.'))

                elif not not_ajax_get:
                    return HttpResponseBadRequest(_('This method works with AJAX only.'))

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)

    return decorator
