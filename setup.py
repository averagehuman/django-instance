#!/usr/bin/env python
import os
import sys
import re
from ast import literal_eval
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

rx_version = re.compile(r'__version__\s*=\s*(.*)')

invalid = lambda s: not s or s.isspace() or s[0] == '#'

def filtered(file):
    for line in read(file).splitlines():
        if not invalid(line):
            yield line

def read(filepath):
    root = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(root, filepath)
    with open(filepath, 'rb') as f:
        return f.read().decode('utf8')

class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)

VERSION = str(
    literal_eval(rx_version.search(read('instance/__init__.py')).group(1))
)
README = read('README.rst')
CHANGELOG = read('docs/changelog.rst')
ENTRY_POINTS = '''
[console_scripts]
instance=instance.cli:main
django=instance.cli:manage
django-server=instance.cli:serve
'''
REQUIRES = [
    s.rpartition('#egg=')[2].strip() for s in filtered('requirements.txt')
]

setup(
    name="django-instance",
    version=VERSION,
    description="An alternative Django CLI",
    author="gmf",
    author_email = "gmflanagan@outlook.com",
    long_description=README + '\n' + CHANGELOG,
    url="https://github.com/averagehuman/django-instance",
    license="BSD",
    packages = find_packages(),
    include_package_data=True,
    tests_require=['tox', 'musette', 'django_extensions'],
    cmdclass = {'test': Tox},
    entry_points=ENTRY_POINTS,
    install_requires=REQUIRES,
)

