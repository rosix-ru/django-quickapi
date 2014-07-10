# -*- coding: utf-8 -*-
#
#  quickapi/utils.py
#  
#  Copyright 2014 Grigoriy Kramarenko <root@rosix.ru>
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

from django.utils import six
from django.utils.translation import lazy, ugettext_lazy as _


def _apidoc_lazy(header, params=_('Nothing'), data='', footer=''):
    """
    Returns formatted documentation by generic template.
    """

    template = _("""
%(header)s

#### Request parameters

%(params)s

#### Returned object

%(data)s

%(footer)s

""")
    return template % {'header':header, 'params':params, 'data':data, 'footer':footer}

apidoc_lazy = lazy(_apidoc_lazy, six.text_type)

def _combine_string(string, args=None):
    """
    Combines a template string with the passed arguments
    """
    if args is None:
        return string
    return string % args

string_lazy = lazy(_combine_string, six.text_type)



