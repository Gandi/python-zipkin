import os
import re
import sys
from setuptools import setup, find_packages

name = 'zipkin'
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()
with open(os.path.join(here, name, '__init__.py')) as version:
    VERSION = re.compile(r".*__version__ = '(.*?)'",
                         re.S).match(version.read()).group(1)

requires = [
    'thriftpy',
    'six',
    ]

tests_require = [
    'mock'
    ]

if sys.version_info[:2] < (2, 7):
    tests_require.append('unittest2')

extras_require = {
    'pyramid': [
        'pyramid',
    ],
    'celery': [
        'celery >= 3.1',
    ],
    'requests': [
        'requests',
    ],
    'flask': [
        'flask', 'blinker',
    ],
    'dev': ['pyramid', 'celery', 'requests', 'flask', 'sphinx'],
    'test': tests_require,
}

setup(name='zk',
      version=VERSION,
      description='zipkin',
      long_description=README + '\n\n' + CHANGES,
      classifiers=['Programming Language :: Python',
                   ],
      author='Gandi',
      author_email='feedback@gandi.net',
      url='',
      keywords='zipkin metrics trace',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      extras_require=extras_require,
      tests_require=tests_require,
      test_suite='{name}.tests'.format(name=name),
      )
