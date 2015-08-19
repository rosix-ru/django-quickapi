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

from importlib import import_module
import sys

from django.utils import six

from quickapi.conf import QUICKAPI_DEFINED_METHODS
    

class Collection(object):
    """
    Класс, реализующий отсортированный словарь методов
    """

    def __init__(self):
        self._COLLECTION = {}
        self._CHAIN      = []

    def __bool__(self):
        return bool(self._CHAIN)

    def __len__(self):
        return len(self._CHAIN)

    def __setitem__(self, name, value):
        self._COLLECTION[name] = value
        if name not in self._CHAIN:
            self._CHAIN.append(name)

    def __setattr__(self, name, value):
        if name in ('_COLLECTION', '_CHAIN'):
            return super(Collection, self).__setattr__(name, value)
        self.__setitem__(name, value)

    def __getitem__(self, name):
        return self._COLLECTION[name]

    def __contains__(self, name):
        return name in self._COLLECTION

    def __getattr__(self, name):
        if name in ('_COLLECTION', '_CHAIN'):
            return super(Collection, self).__getattr__(name, value)
        return self.__getitem__(name)

    def __delitem__(self, name):
        del self._COLLECTION[name]
        del self._CHAIN[self._CHAIN.index(name)]

    def __delattr__(self, name):
        if name in ('_COLLECTION', '_CHAIN'):
            raise AttributeError('Is internal attribute')
        self.__delitem__(name)

    def items(self):
        return [(name, self._COLLECTION[name]) for name in self._CHAIN]

    def keys(self):
        return self._CHAIN

    def values(self):
        return [self._COLLECTION[name] for name in self._CHAIN]

    def sort(self):
        self._CHAIN.sort()


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    
    This code is taken from Django 1.7
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        msg = "%s doesn't look like a module path" % dotted_path
        six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError:
        msg = 'Module "%s" does not define a "%s" attribute/class' % (
            dotted_path, class_name)
        six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])


def get_methods(list_or_dict=QUICKAPI_DEFINED_METHODS, sort=True):
    """ Преобразует словарь или список заданных строками методов,
        реальными объектами функций.
        Форматы list_or_dict:
        (('',''),('',''))
        либо
        [['',''],['','']]
        либо
        {'':'', '':''}
    """
    collection = Collection()

    if isinstance(list_or_dict, (list, tuple)):
        seq = list_or_dict
    elif isinstance(list_or_dict, dict):
        sort = True
        seq = list_or_dict.items()
    else:
        raise ValueError('Parameter must be sequence or dictionary')

    for key,val in seq:
        if isinstance(val, six.string_types):
            method = import_string(val)
        else:
            method = val

        collection[key] = {
            'method': method,
            'doc':    method.__doc__,
            'name':   key,
            'namespace': key.split('.')[0] if '.' in key else None
        }

    if sort:
        collection.sort()

    return collection


