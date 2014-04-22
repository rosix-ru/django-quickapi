# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import template
from django.utils.encoding import smart_text
register = template.Library()

try:
    # Проверка установленного в системе markdown.
    from markdown import markdown
except:
    markdown_support = False
    markdown = None
else:
    markdown_support = True

try:
    # Проверка установленного в системе pygments.
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter
except:
    highlight_support = False
    highlight = None
    get_lexer_by_name = None
    HtmlFormatter = None
else:
    highlight_support = True

def drop_space(doc):
    """
    Удаление начальных и конечных пробелов в документации.
    Выравнивает весь код по первой его строке.
    """
    L = []
    cut = None
    start_code = False
    for s in doc.split('\n'):
        # Если начинается код
        if s.strip(' ').startswith('`'):
            cut = len(s[:s.find('`')]) # только выставляем обрезку
            start_code = True          # устанавливаем начальный флаг
        # Если заканчивается код
        if s.strip().endswith('`') and not start_code:
            L.append(s[cut:])          # то записываем,
            cut = None                 # сбрасываем обрезку
            start_code = False         # сбрасываем начальный флаг
            continue                   # и прерываем цикл
        # Теперь записываем
        if not cut is None:
            L.append(s[cut:])          # с обрезкой
        else:
            L.append(s.strip(' '))     # или полностью очищенную строку
    return '\n'.join(L)

def highlight_prepare(text):
    """
    Обработка подстветки синтаксиса с помощью Pygments
    """
    TEXT = []
    MARK = []
    CODE = []
    start_code = False
    is_code = False
    lexer = None
    formatter = HtmlFormatter()

    for s in text.split('\n'):
        # Если начинается код
        if s.startswith('```') and not is_code:
            start_code = is_code = True # ставим флаги
            if markdown_support and MARK:
                # добавляем текст markdown
                try:
                    mark = markdown('\n'.join(MARK))
                except:
                    mark = ''
                TEXT.append(mark)
                MARK = [] # сбрасываем текст markdown
            continue # и прерываем цикл
        # Если закончился код
        elif s.startswith('```') and is_code:
            is_code = False # ставим флаги
            try:
                # Подсвечиваем код
                code = highlight('\n'.join(CODE), lexer, formatter)
            except:
                code = ''
            # Добавляем код в текст
            TEXT.append(code)
            CODE = []
            lexer = None
        # Если это первая строка кода
        elif start_code:
            if not s.startswith('#!'):
                raise ValueError('%s not start with #!' % s)
            # Устанавливем язык
            lexer = get_lexer_by_name(s.strip(' ').strip('#!'))
            start_code = False
            continue
        # Если это строка из кода
        elif is_code:
            CODE.append(s)
        elif markdown_support:
            MARK.append(s)
        else:
            TEXT.append(s)

    # Если что то осталось в markdown
    if markdown_support and MARK:
        # добавляем текст markdown
        try:
            mark = markdown('\n'.join(MARK))
        except:
            mark = ''
        TEXT.append(mark)

    return '\n'.join(TEXT)


@register.filter
def formatdoc(text):
    text = drop_space(smart_text(text))
    if highlight_support:
        text = highlight_prepare(text)
    elif markdown_support:
        text = markdown(text)
    else:
        '<br>'.join(text.split('\n'))
    return text
