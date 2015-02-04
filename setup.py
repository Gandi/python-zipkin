import os
import re
from setuptools import setup, find_packages

name='zipkin'
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()
with open(os.path.join(here, name, '__init__.py')) as version:
    VERSION = re.compile(r".*__version__ = '(.*?)'",
                         re.S).match(version.read()).group(1)

requires = [
    'thrift',
    'facebook-scribe',
    ]

test_requires = ['nose']

extras_require = {
    'pyramid': [
        'pyramid',
    ],
    'celery': [
        'celery',
    ],
    'requests': [
        'requests',
    ],
    'dev': ['pyramid', 'celery', 'requests'],
    'test': test_requires,
}

setup(name=name,
      version=VERSION,
      description='zipkin',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      extras_require=extras_require,
      tests_require=test_requires,
      test_suite='{name}.tests'.format(name=name),
      )
