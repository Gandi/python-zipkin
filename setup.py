import os
import re
import sys
from setuptools import setup, find_packages

name = "zipkin"
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.rst")) as f:
    README = f.read()
with open(os.path.join(here, "CHANGES.rst")) as f:
    CHANGES = f.read()
with open(os.path.join(here, name, "__init__.py")) as version:
    VERSION = (
        re.compile(r'.*__version__ = "(.*?)"', re.S).match(version.read()).group(1)
    )

requires = [
    "thriftpy2",
    "six",
]

tests_require = ["pytest", "mock"]

if sys.version_info[:2] < (2, 7):
    tests_require.append("unittest2")

extras_require = {
    "django": [
        "django",
    ],
    "pyramid": [
        "pyramid",
    ],
    "celery": [
        "celery >= 3.1",
    ],
    "requests": [
        "requests",
    ],
    "psycopg2": [
        "psycopg2-binary",
    ],
    "flask": [
        "flask",
        "blinker",
    ],
    "dev": [
        "blinker",
        "celery",
        "django",
        "flask",
        "psycopg2-binary",
        "pyramid",
        "requests",
        "sphinx",
        "sqlalchemy",
    ],
    "test": tests_require,
}

setup(
    name="zk",
    version=VERSION,
    description="zipkin",
    long_description=README + "\n\n" + CHANGES,
    classifiers=[
        "Programming Language :: Python",
    ],
    author="Gandi",
    author_email="feedback@gandi.net",
    url="",
    keywords="zipkin metrics trace",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extras_require=extras_require,
    tests_require=tests_require,
    test_suite="{name}.tests".format(name=name),
)
