# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import base64

from django.apps import apps
from django.conf import settings
from django.test import TestCase
from django.utils import six


User = apps.get_model(settings.AUTH_USER_MODEL)
QUICKAPI_URL = getattr(settings, 'TEST_QUICKAPI_URL', '/api/')
USERNAME = getattr(settings, 'TEST_QUICKAPI_USERNAME', 'quickapi')
PASSWORD = getattr(settings, 'TEST_QUICKAPI_PASSWORD', 'quickapi')


class QuickapiTestCase(TestCase):
    url = QUICKAPI_URL

    def assertJsonContent(self, content, msg=None, status=None, data=None, message=None):
        """
        Проверка контента ответа QuickAPI.

        Параметр `mgs` передаётся для генерации сообщения об ошибке 
        получения корректных данных. Остальные параметры - для 
        диагностики самого контента.

        Возвращает данные, полученные внутри контента (ключ `data`).
        """

        try:
            r = json.loads(content)
        except ValueError:
            r = content

        self.assertIsInstance(r, dict, msg)

        self.assertIn('status', r)
        if status is not None:
            self.assertEqual(r['status'], status)

        self.assertIn('data', r)
        if data is not None:
            self.assertEqual(r['data'], data)

        self.assertIn('message', r)
        if data is not None:
            self.assertEqual(r['message'], message)

        return r['data']


class SimpleTest(QuickapiTestCase):

    def setUp(self):
        self.user = User.objects.create_user(username=USERNAME, password=PASSWORD)

    def test_warning_auth(self):
        """
        Тестирование опасной передачи параметров аторизации в GET-запросе.
        """
        response = self.client.get(self.url, {
            'method': 'quickapi.test',
            'username': USERNAME,
            'password': PASSWORD,
        })
        self.assertEqual(response.status_code, 400)

    def test_not_authenticated(self):
        """
        Тестирование метода без авторизации.

        Зависит от настроек QuickAPI, если страница задекорирована
        с помощью `quickapi.decorators.auth_required`, то вернёт 401 код.
        """
        response = self.client.get(self.url, {'method': 'quickapi.test'})
        if response.status_code == 200:
            data = self.assertJsonContent(response.content)
            self.assertEqual(data['is_authenticated'], False)
        else:
            self.assertEqual(response.status_code, 401)

    def test_authenticated(self):
        """
        Тестирование вариантов авторизации.
        """
        auth = self.client.login(username=USERNAME, password='')
        self.assertEqual(auth, False)

        auth = self.client.login(username=USERNAME, password=PASSWORD)
        self.assertEqual(auth, True)
        self.client.logout()

        with self.settings(QUICKAPI_ONLY_AUTHORIZED_USERS=True):
            # Простая POST авторизация
            response = self.client.post(self.url, {
                'method': 'quickapi.test',
                'username': USERNAME,
                'password': PASSWORD,
            })
            self.assertEqual(response.status_code, 200)
            self.client.logout()

            # подготовка basic-авторизации
            s = '%s:%s' % (USERNAME, PASSWORD)
            if six.PY3:
                b = bytes(s, 'utf-8')
            else:
                b = bytes(s.encode('utf-8'))

            basic = b'Basic ' + base64.b64encode(b)

            # GET c заголовком 'HTTP_AUTHORIZATION'
            response = self.client.get(self.url, {'method': 'quickapi.test'}, HTTP_AUTHORIZATION=basic)
            self.assertEqual(response.status_code, 200)
            self.client.logout()

            # POST c заголовком 'HTTP_AUTHORIZATION'
            response = self.client.post(self.url, {'method': 'quickapi.test'}, HTTP_AUTHORIZATION=basic)
            self.assertEqual(response.status_code, 200)
            self.client.logout()

            # GET c заголовком 'HTTP_X_AUTHORIZATION'
            response = self.client.get(self.url, {'method': 'quickapi.test'}, HTTP_X_AUTHORIZATION=basic)
            self.assertEqual(response.status_code, 200)
            self.client.logout()

            # POST c заголовком 'HTTP_X_AUTHORIZATION'
            response = self.client.post(self.url, {'method': 'quickapi.test'}, HTTP_X_AUTHORIZATION=basic)
            self.assertEqual(response.status_code, 200)

            # parsing response
            data = self.assertJsonContent(response.content)
            self.assertEqual(data['is_authenticated'], True)

            self.client.logout()

    def test_get_page_or_method(self):
        """
        Тестирование получения страницы quickapi или результата метода.
        """
        # GET page without authentication
        response = self.client.get(QUICKAPI_URL)
        self.assertEqual(response['Content-Type'], 'text/html; charset=%s' % settings.DEFAULT_CHARSET)

        # Authentication
        auth = self.client.login(username=USERNAME, password=PASSWORD)
        self.assertEqual(auth, True)

        # GET method
        response = self.client.get(self.url, {'method': 'quickapi.test'})
        self.assertEqual(response['Content-Type'], 'application/json; charset=%s' % settings.DEFAULT_CHARSET)

        # POST method
        response = self.client.post(self.url, {'method': 'quickapi.test'})
        self.assertEqual(response['Content-Type'], 'application/json; charset=%s' % settings.DEFAULT_CHARSET)

        data = self.assertJsonContent(response.content)
        self.assertEqual(data['is_authenticated'], True)



