# -*- coding: utf-8 -*-
#
#  quickapi/utils/filters.py
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
import operator

from django.db.models import Q


def construct_search(field_name):
    """
    Вспомогательная функция для построения поисковых полей
    """
    if field_name.startswith('^'):
        return "%s__istartswith" % field_name[1:]
    elif field_name.startswith('='):
        return "%s__iexact" % field_name[1:]
    elif field_name.startswith('@'):
        return "%s__search" % field_name[1:]

    return "%s__icontains" % field_name


def filter_queryset(queryset, search_fields, query):
    """
    Фильтрация по нескольким полям
    """
    if search_fields and not query in ('', None, False, True):

        orm_lookups = [construct_search(str(search_field))
                       for search_field in search_fields]

        for bit in query.split():
            or_queries = [Q(**{orm_lookup: bit})
                          for orm_lookup in orm_lookups]
            queryset = queryset.filter(reduce(operator.or_, or_queries))

    return queryset


