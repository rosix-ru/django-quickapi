# coding: utf-8
"""
Содержит базовый класс для построения клиентов, взаимодействующих
с QuickAPI v2 и выше. Работает с Python 2/3.

Пример использования:

from quickapi.client import BaseClient

kw = {
    'url': 'https://example.org/api/',
    # можно сразу установить все остальные параметры:
    # `username`, `password`, `timeout`, `cookie_filename` и т.д.
}

# один экземпляр для всех вызываемых методов
api = BaseClient(**kw)

# Включение вывода заголовков ответа
api.print_info = True

# Неавторизованнный пользователь
data = api.method('quickapi.test')

# Установка файла с куками
api.set_cookiejar('cookies.txt')

api.username = 'login'
api.password = 'passw'

# С попыткой авторизации пользователя
data = api.method('quickapi.test')

# Далее авторизация будет проходить по кукам, а данные лучше скрыть.
api.username = None
api.password = None

# Тест вызова ошибки
data = api.method('quickapi.test', code=500)

"""

from __future__ import unicode_literals, print_function

import json
import six
import zlib

if six.PY3:
    from urllib.parse import urlencode
    from urllib.request import Request, build_opener, HTTPCookieProcessor
    from http.cookiejar import MozillaCookieJar
else:
    from urllib import urlencode
    from urllib2 import Request, build_opener, HTTPCookieProcessor
    from cookielib import MozillaCookieJar


class BaseClient(object):
    """
    Базовый класс для работы с удалённым API
    """

    username = None
    password = None
    url      = 'http://localhost:8000/api/'
    headers  = {"Content-type": "application/json", "Accept": "application/json"}
    timeout  = 10000
    cookiejar = None
    print_info = False
    code_page = 'utf-8'


    def __init__(self, cookie_filename=None, **kwargs):

        for key, val in kwargs.items():
            setattr(self, key, val)
        
        if cookie_filename:
            self.set_cookiejar(cookie_filename)
    
    def set_cookiejar(self, name):
        self.cookiejar = MozillaCookieJar(name)
        try:
            self.cookiejar.load()
        except IOError:
            self.cookiejar.save()

    def get_request(self, data, **kwargs):
        """
        Возвращает новый объект запроса.
        """

        params = urlencode({'jsonData': data})
        params = params.encode('ascii')
        request = Request(url=self.url, data=params, headers=self.headers)

        return request

    def get_response(self, request, openerargs=(), **kwargs):
        """
        Возвращает новый обработчик запроса и устанавливает куки.
        """

        if not self.cookiejar is None:
            cookiehand = HTTPCookieProcessor(self.cookiejar)
            openerargs = (cookiehand,) + openerargs

        opener = build_opener(*openerargs)

        try:
            response = opener.open(request, timeout=self.timeout)
        except IOError as e:
            raise e

        if not self.cookiejar is None:
            self.cookiejar.save()

        return response

    def get_result(self, data, **kwargs):
        """
        Запрашивает данные из API
        """

        jsondata = json.dumps(data)

        request = self.get_request(jsondata)
        response = self.get_response(request)
        if self.print_info:
            print('Status: %s' % response.code)
            print(response.info())

        data = response.read()

        try:
            return zlib.decompress(data)
        except:
            return data

    def json_loads(self, data, **kwargs):
        """
        Переобразовывает JSON в объекты Python, учитывая кодирование
        """

        data = data.decode(self.code_page)
        data = json.loads(data)

        return data

    def prepare_data(self, data, **kwargs):
        """
        Предназначен для переопределения в наследуемых классах.
        Здесь просто добавляются учётные данные.
        """
        if self.username:
            data['username'] = self.username 
            data['password'] = self.password 

        return data

    def clean(self, data, **kwargs):
        """
        Преобразует полученные данные
        """

        data = self.json_loads(data)

        if data is None:
            return data

        status = data.get('status', None)

        if status != 200:
            msg = data.get('message', None)
            if msg:
                if six.PY3:
                    error = '%s - %s' % (status, msg)
                else:
                    error = b'%s - %s' % (status, msg.encode(self.code_page))
            else:
                error = data

            raise ValueError(error)

        return data['data']

    def method(self, method, **kwargs):
        """
        Вызывает метод API и возвращает чистые данные
        """
        data = {'method': method, 'kwargs': kwargs}
        data = self.prepare_data(data)
        data = self.get_result(data)
        data = self.clean(data)
        return data


    
    
