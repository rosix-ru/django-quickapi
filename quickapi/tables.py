# -*- coding: utf-8 -*-
#
#  quickapi/tables.py
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
import operator

from django.db.models import Q
from django.core.paginator import Paginator#, InvalidPage, EmptyPage
from django.utils import six
from django.utils.encoding import force_text

from quickapi.utils.filters import filter_queryset


class QuickTable(object):
    """
    Class for prepare JSON data for QuickTables
    """
    manager = None
    columns = ()
    order_columns = ()
    global_search_columns = ()
    custom_search_columns = ()
    custom_exact_columns  = ()
    ajax_url_column = None
    global_filter_key = '_search_'
    max_display_length = 100  # max limit of records returned, do not
                              # allow to kill our server by huge sets
                              # of data


    def map_column(self, name):
        """
        Производит сопоставление названия колонки к полю в базе данных.
        Для наследуемых классов.
        """
        return name


    def render_column(self, request, row, column):
        """
        Renders a column on a row
        """
        if column in ('__unicode__', '__str__'):
            return force_text(row)

        column = column.replace('__', '.')

        if hasattr(row, 'get_%s_display' % column):
            # It's a choice field
            data = getattr(row, 'get_%s_display' % column)()
        else:
            try:
                data = getattr(row, column)
            except AttributeError:
                obj = row
                for part in column.split('.'):
                    if obj is None:
                        break
                    obj = getattr(obj, part)

                data = obj

        if self.ajax_url_column and column == self.ajax_url_column and hasattr(row, 'get_absolute_url'):
            return '<a href="#ajax%s">%s</a>' % (row.get_absolute_url(), data)
        else:
            return data


    def render_objects(self, request, qs):
        return map(lambda o: dict([(c, self.render_column(request, o, c)) for c in self.columns]), qs)


    def filtering(self, request, qs, filters):
        """
        Производит фильтрацию набора данных
        """
        for f, query in six.iteritems(filters):

            if f == self.global_filter_key:
                qs = filter_queryset(qs, self.global_search_columns, query)

            elif f in self.custom_search_columns:
                qs = filter_queryset(qs, (self.map_column(f),), query)

            elif f in self.custom_exact_columns:
                qs = qs.filter(Q(**{'{0}__exact'.format(self.map_column(f)): query}))

        return qs


    def ordering(self, request, qs, ordering):
        """
        Функция проверяет параметры сортировки и применяет только валидную
        """

        ordering = [ o for o in ordering
            if (o and not o.startswith('--') and o.lstrip('-') in self.order_columns)
        ]

        if ordering:
            return qs.order_by(*ordering)

        return qs


    def paging(self, request, qs, page, limit, orphans=0):
        """
        Функция возвращает объект Page паджинатора
        """
        return Paginator(qs, per_page=limit, orphans=orphans).page(page)


    def get_info(self, request, qs):
        """
        Возвращает информацию о наборе. Для наследования.
        """
        return None


    def get_context_data(self, request, page, info):
        data =  {
            'objects': self.render_objects(request, page.object_list),
            'page': page.number,
            'num_pages': page.paginator.num_pages,
            'info': info,
        }

        return data


    def method(self, request, filters, ordering, page, limit):
        """
        Стандартное получение данных. Для наследования.
        """
        if not self.manager:
            raise NotImplementedError("Not specified a model Manager.")

        if not self.columns:
            raise NotImplementedError("Not specified columns.")

        qs   = self.manager.all()
        qs   = self.filtering(request, qs, filters)
        info = self.get_info(request, qs)
        qs   = self.ordering(request, qs, ordering)
        page = self.paging(request, qs, page, limit)

        return self.get_context_data(request, page, info)


