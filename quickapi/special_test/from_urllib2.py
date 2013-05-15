#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
import json, urllib2, base64

########################################################################
#                  Настройка адреса сервера API                        #
########################################################################
SCHEME       = 'http'
HOST         = 'localhost'
PORT         = 8000
API          = '/api/'

########################################################################
#                      Настройка авторизации                           #
########################################################################
USERNAME     = 'admin'
PASSWORD     = 'admin'

# Простая авторизация, когда прямо в запросе указаны персональные данные. 
# Это абсолютно рабочий метод, когда другие могут требовать специальных
# настроек вэб-сервера
SIMPLE_AUTH  = False

# Принудительно устанавливать заголовок для Basic-авторизации, если не
# рабоатет стандартный режим
FORCE_BASIC_HEADERS = True

########################################################################
#                               КОД                                    #
########################################################################
DEBUG = True
class BaseAPI(object):
    version  = None
    hostname = HOST
    port     = PORT
    username = USERNAME
    password = PASSWORD
    port     = PORT
    scheme   = SCHEME
    headers  = {
        "Accept":         "application/json",
        "Accept-Charset": "utf-8",
        "Content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    timeout  = 1000
    error    = None

    def __init__(self, **kwargs):
        """ Инициализация """
        for key, val in kwargs:
            setattr(self, key, val)

        # Нельзя работать без указания API
        if self.version is None:
            raise NotImplemented(u'Not set API version')

        # Принудительный заголовок для Basic-авторизации
        if FORCE_BASIC_HEADERS and self.username and self.password:
            self.headers['Authorization'] = 'Basic ' + \
                base64.b64encode('%s:%s' % (self.username, self.password))

    @property
    def netloc(self):
        """ Спецификатор местоположения в сети """
        if self.port:
            return '%s:%s' % (self.hostname, self.port)
        else:
            return self.hostname

    @property
    def path(self):
        """ Путь согласно версии API """
        return self.version

    @property
    def params(self):
        """ При необходимости переопределяемое свойство в наследуемых
            классах
        """
        return ''

    @property
    def query(self):
        """ При необходимости переопределяемое свойство в наследуемых
            классах
        """
        return ''

    @property
    def fragment(self):
        """ При необходимости переопределяемое свойство в наследуемых
            классах
        """
        return ''

    @property
    def url(self):
        """ Возвращает адрес URL. """
        return urllib2.urlparse.ParseResult(
                self.scheme, self.netloc, self.path,
                self.params, self.query, self.fragment).geturl()

    @property
    def format_error(self):
        """ Выводит ошибку в презентабельном виде """
        return unicode(traceback.format_exc(self.error))

    def get_request(self, data, **kwargs):
        """ Возвращает новый объект запроса. """
        return urllib2.Request(url=self.url, data=data, headers=self.headers)

    def get_opener(self, **kwargs):
        """ Возвращает новый обработчик запроса с Basic аутентификацией,
            если установлены атрибуты, идентифицирующие пользователя.
        """
        args = []
        if self.username and self.password and not SIMPLE_AUTH:
            auth = urllib2.HTTPBasicAuthHandler()
            auth.add_password("realm", self.hostname, self.username, self.password)
            args.append(auth)
        return urllib2.build_opener(*args)

    def get_result(self, data, **kwargs):
        """ Запрашивает данные из API """
        jsondata = json.dumps(data, ensure_ascii=False).encode(
                                                    'utf8', 'ignore')
        request = self.get_request(jsondata)
        handler_debug(**request.__dict__)
        opener = self.get_opener() # store
        #~ handler_debug(**opener.__dict__)
        try:
            data = opener.open(request, timeout=self.timeout).read()
            handler_debug(data)
        except Exception as e:
            self.error = e
            print self.format_error
            data = None
        opener.close()
        return data

    def json_loads(self, data, **kwargs):
        """ Переобразовывает JSON в объекты Python, учитывая кодирование"""
        try:
            data = json.loads(data.decode('zlib'))
        except:
            try:
                data = json.loads(data)
            except:
                data = None
        return data

    def prepare_data(self, data, **kwargs):
        """ Переопределяемый метод в наследуемых классах.
            Предварительно конвентирует отправляемые данные.
        """
        if SIMPLE_AUTH:
            data['username'] = self.username 
            data['password'] = self.password 
        return data

    def clean(self, data, **kwargs):
        """ Переопределяемый метод в наследуемых классах.
            По-умолчанию просто конвертирует из строки JSON  """
        return self.json_loads(data)

    def method(self, method, **kwargs):
        """ Вызывает метод API и возвращает чистые данные """
        data = {'method': method, 'kwargs': kwargs}
        handler_debug(**data)
        data = self.prepare_data(data)
        data = self.get_result(data)
        data = self.clean(data)
        return data

class Version(BaseAPI):
    version = API

    def clean(self, data, **kwargs):
        """ Преобразует полученные данные """
        data = self.json_loads(data)
        if data is None:
            return data
        status = data.get('status', None)
        if status != 200:
            print data.get('message')
        return data['data']

def handler_debug(*args, **kwargs):
    if DEBUG:
        print '\nDEBUG >>>'
        for x in args:
            print x
        for k,v in kwargs.items():
            print k, '=', v
        print '<<< DEBUG'

def main(method=None, simple=False):
    api = Version()
    if not simple:
        print api.method(method or 'test')
    else:
        url = api.url
        
        data = {'username': USERNAME,'password':PASSWORD,
                'method': method or 'test',
                'kwargs': {}, 
        }
        r = urllib2.Request(url, headers=api.headers)
        r = urllib2.urlopen(r, data=json.dumps(data))
        print r.read()

########################################################################

if __name__ == '__main__':
    main()
