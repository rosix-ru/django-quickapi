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
from functools import wraps

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseBadRequest, HttpResponseServerError


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    This decorator different from those in Django that checks is
    active user or not.
    """

    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_authenticated(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )

    if function:
        return actual_decorator(function)

    return actual_decorator


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
