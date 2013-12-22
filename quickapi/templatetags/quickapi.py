# -*- coding: utf-8 -*-
"""
###############################################################################
# Copyright 2012 Grigoriy Kramarenko.
###############################################################################
# This file is part of QUICKAPI.
#
#    QUICKAPI is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    QUICKAPI is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with QUICKAPI.  If not, see <http://www.gnu.org/licenses/>.
#
# Этот файл — часть QUICKAPI.
#
#   QUICKAPI - свободная программа: вы можете перераспространять ее и/или
#   изменять ее на условиях Стандартной общественной лицензии GNU в том виде,
#   в каком она была опубликована Фондом свободного программного обеспечения;
#   либо версии 3 лицензии, либо (по вашему выбору) любой более поздней
#   версии.
#
#   QUICKAPI распространяется в надежде, что она будет полезной,
#   но БЕЗО ВСЯКИХ ГАРАНТИЙ; даже без неявной гарантии ТОВАРНОГО ВИДА
#   или ПРИГОДНОСТИ ДЛЯ ОПРЕДЕЛЕННЫХ ЦЕЛЕЙ. Подробнее см. в Стандартной
#   общественной лицензии GNU.
#
#   Вы должны были получить копию Стандартной общественной лицензии GNU
#   вместе с этой программой. Если это не так, см.
#   <http://www.gnu.org/licenses/>.
###############################################################################
"""
from django import template
from django.utils.encoding import smart_unicode
register = template.Library()

try:
    # Проверка установленного в системе markdown.
    from markdown import markdown as _markdown
except:
    markdown = lambda x: x
    BIT = '<br>'
else:
    markdown = lambda x: _markdown(x)
    BIT = '\n'

def drop_space(doc):
    """ Удаление начальных и конечных пробелов в документации.
        Обратное слияние строк в текст зависит от наличия markdown
        в системе.
        
        Выравнивает весь код по первой его строке.
    """
    L = []
    cut = None
    for s in doc.split('\n'):
        # Если начинается код
        if s.strip(' ').startswith('`'):
            cut = len(s[:s.find('`')]) # только выставляем обрезку
        # Если заканчивается код
        if s.strip().endswith('`'):
            L.append(s[cut:])          # то записываем,
            cut = None                 # сбрасываем обрезку
            continue                   # и прерываем цикл
        # Теперь записываем
        if not cut is None:
            L.append(s[cut:])          # с обрезкой
        else:
            L.append(s.strip(' '))     # или полностью очищенную строку
    return BIT.join(L)

@register.filter
def formatdoc(text):
    text = drop_space(smart_unicode(text))
    try:
        text = markdown(text)
    except:
        pass
    return text
