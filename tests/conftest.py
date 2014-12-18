from __future__ import absolute_import, unicode_literals
import os
import shutil
from tempfile import mkdtemp

import pytest

from instance.cli.application import UI
from instance.utils import BytesIO

here = os.path.abspath(os.path.dirname(__file__))
SITE_UID = 'instance-test'

@pytest.fixture(scope="session")
def env():
    from instance.conf import settings, DATA_ROOT_VARIABLE, SITE_UID_VARIABLE
    from django.conf import settings as django_settings
    assert not settings.configured
    assert not django_settings.configured
    settings.configure(overrides={
        DATA_ROOT_VARIABLE: here,
        SITE_UID_VARIABLE: SITE_UID
    })
    return settings

@pytest.fixture
def ui(env):
    return UI(stdout=BytesIO(), stderr=BytesIO())

@pytest.fixture
def File():
    def FileOpener(relpath, mode="rb"):
        return open(os.path.join(data_root, relpath.lstrip('/')), mode)
    return FileOpener

@pytest.fixture
def rf(env):
    from django.test.client import RequestFactory
    return RequestFactory()

@pytest.fixture
def client(env):
    from django.test.client import Client
    return Client()

