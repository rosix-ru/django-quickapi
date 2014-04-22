# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseBadRequest
from functools import wraps

def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.is_authenticated(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def api_required(view_func):
    """ Декоратор для представлений, работающих только с API. """
    @wraps(view_func)
    def check(request, *args, **kwargs):
        if not request.is_ajax() and not (request.method == 'POST'):
            return HttpResponseBadRequest()
        else:
            return view_func(request, *args, **kwargs)
    return check
