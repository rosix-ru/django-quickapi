from setuptools import setup, find_packages
import os
import quickapi

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
README = read('README')

setup(
    name='django-quickapi',
    version=quickapi.__version__,
    description='The Django-application for the fast organization API.',
    long_description=README,
    author='Grigoriy Kramarenko',
    author_email='root@rosix.ru',
    url='http://develop.rosix.ru/django-quickapi/',
    license='GNU General Public License v3 or later (GPLv3+)',
    platforms='any',
    zip_safe=False,
    packages=find_packages(),
    include_package_data = True,
    install_requires=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Framework :: Django',
        'Natural Language :: Russian',
    ],
)
