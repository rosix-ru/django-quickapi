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
import operator

from django.db.models import Q, Model
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
    global_search_columns = () # fields for searching on global_filter_key
    custom_search_columns = () # when searching by one and above fields
    custom_exact_columns  = () # when searching by one and above fields and exact only
    map_columns           = {}
    global_filter_key = '_search_'
    max_display_length = 100  # max limit of records returned, do not
                              # allow to kill our server by huge sets
                              # of data


    def __init__(self, *args, **kwargs):

        self.validate()


    def validate(self):

        if not self.manager:
            raise NotImplementedError("Not specified a model Manager for %s." % self.__class__)

        if not self.columns:
            raise NotImplementedError("Not specified columns for %s." % self.__class__)


    def map_column(self, name):
        """
        Производит сопоставление названия колонки к полю в базе данных.
        Для наследуемых классов.
        """
        return self.map_columns.get(name, name)


    def render_column(self, request, row, column):
        """
        Renders a column on a row
        """

        if column in ('__unicode__', '__str__'):
            return force_text(row)

        column = column.replace('__', '.')

        if hasattr(row, 'get_%s_display' % column):
            # It's a choice field
            return getattr(row, 'get_%s_display' % column)()

        elif '.' in column:
            data = row
            for part in column.split('.'):
                if data is None:
                    break
                data = getattr(data, part, None)

            if isinstance(data, Model):
                return force_text(data)

            return data

        else:
            return getattr(row, column)


    def render_objects(self, request, qs):

        cols = [ self.map_column(c) for c in self.columns ]

        def _serialize(o):
            return { c: self.render_column(request, o, c) for c in cols }

        return map(_serialize, qs)


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
        """
        Формирование контекста JSON структуры
        """
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

        qs   = self.manager.all()
        qs   = self.filtering(request, qs, filters)
        info = self.get_info(request, qs)

        qs   = self.ordering(request, qs, ordering)
        page = self.paging(request, qs, page, limit)

        return self.get_context_data(request, page, info)


