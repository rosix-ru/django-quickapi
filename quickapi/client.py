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

# Не авторизованный пользователь
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
data = api.method('quickapi.test')

# Тест вызова ошибки
data = api.method('quickapi.test', code=500)

"""

from __future__ import unicode_literals, print_function

import json
import six
import zlib
import base64

if six.PY3:
    from urllib.parse import urlencode
    from urllib.request import Request, build_opener, HTTPCookieProcessor
    from http.cookiejar import MozillaCookieJar
else:
    from urllib import urlencode
    from urllib2 import Request, build_opener, HTTPCookieProcessor
    from cookielib import MozillaCookieJar


class RemoteAPIError(ValueError):
    pass


class BaseClient(object):
    """
    Базовый класс для работы с удалённым API
    """

    username = None
    password = None
    url      = 'http://localhost:8000/api/'
    headers  = {
        "Content-type": "application/json",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
    }
    timeout  = 10000
    cookiejar = None
    print_info = False
    code_page = 'utf-8'
    use_basic_auth = False


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

    def get_request(self, data):
        """
        Возвращает новый объект запроса.
        """

        params = urlencode({'jsonData': data})
        params = params.encode('ascii')
        
        headers = {}
        headers.update(self.headers)
        if self.use_basic_auth and self.username and self.password:
            s = '%s:%s' % (self.username, self.password)
            if six.PY3:
                b = bytes(s, 'utf-8')
            else:
                b = bytes(s.encode('utf-8'))

            headers['Authorization'] = b'Basic ' + base64.b64encode(b)
        
        request = Request(url=self.url, data=params, headers=headers)

        return request

    def get_opener(self):
        """
        Возвращает новый обработчик запроса с необходимыми процессорами.
        """
        args = ()

        if not self.cookiejar is None:
            cookiehand = HTTPCookieProcessor(self.cookiejar)
            args += (cookiehand,)

        return build_opener(*args)


    def get_response(self, request):
        """
        Возвращает новый обработчик запроса и устанавливает куки.
        """

        opener = self.get_opener()

        try:
            response = opener.open(request, timeout=self.timeout)
        except IOError as e:
            raise e

        if not self.cookiejar is None:
            self.cookiejar.save()

        return response

    def get_result(self, data):
        """
        Запрашивает данные из API
        """

        if self.print_info:
            print('Kwargs: %s' % data.get('kwargs', {}))

        jsondata = json.dumps(data)

        request = self.get_request(jsondata)

        response = self.get_response(request)
        info = response.info()
        encoding = info.get('Content-encoding', None)

        if self.print_info:
            print('Status: %s' % response.code)
            print(info)

        data = response.read()

        if encoding in ('gzip', 'deflate'):
            try:
                return zlib.decompress(data)
            except:
                return data

        return data

    def json_loads(self, data):
        """
        Переобразовывает JSON в объекты Python, учитывая кодирование
        """

        data = data.decode(self.code_page)
        data = json.loads(data)

        return data

    def prepare_data(self, data):
        """
        Предназначен для переопределения в наследуемых классах.
        Здесь просто добавляются учётные данные.
        """
        if self.username and not self.use_basic_auth:
            data['username'] = self.username 
            data['password'] = self.password 

        return data

    def clean(self, data):
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

            raise RemoteAPIError(error)

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


    
    
