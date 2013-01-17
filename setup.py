import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-quickapi',
    version='0.1',
    description='The Django-application for the fast organization API.',
    long_description=read('README'),
    author='Grigoriy Kramarenko',
    author_email='root@rosix.ru',
    url='http://develop.rosix.ru/django-quickapi/',
    packages=['quickapi'],
    license='GNU General Public License, Version 3',
)
