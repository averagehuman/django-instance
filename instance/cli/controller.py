# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import shutil

try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO

import logbook

from django.utils.text import slugify
from django.core.management import call_command

from instance.conf import settings, SITE_STORAGE_ROOT_VARIABLE
from instance.utils import pathjoin, pathexists, text_type, mkdir, dirname

log = logbook.Logger(__name__)

class UIError(Exception):
    pass

class PathExists(UIError):
    
    def __str__(self):
        return "path exists '%s'" % self.args[0]

class PathDoesNotExist(UIError):
    
    def __str__(self):
        return "invalid path '%s'" % self.args[0]

class Writer(object):

    def __init__(self, stream=None, encoding='utf-8'):
        self.stream = stream or BytesIO()

    def write(self, text=''):
        self.stream.write(text.encode(self.encoding))
        self.stream.write('\n')

class SiteController(object):

    def __init__(self, site=None):
        from instance.models import DjangoSite
        self._site = site
        self._cls = DjangoSite

    def exists(self, uid):
        return self._cls.objects.filter(uid__iexact=uid).count() > 0

    def init_site(self, uid, name, fqdn, title=None):
        cls = self._cls
        try:
            site = cls.objects.get(uid__iexact=uid)
        except cls.DoesNotExist:
            site = cls.objects.create(
                uid=uid, name=name, title=title or name,
                fqdn=fqdn,
            )
            log.info("created site '%s'" % site)
        settings.init_site(site)
        self.set_default(site.uid)

    def set_default(self, uid):
        self._cls.objects.set_default(uid)

    def remove_site(self, uid):
        try:
            self._cls.objects.get(uid__iexact=uid).delete()
        except self._cls.DoesNotExist:
            raise UIError("invalid site uid: '%s'" % uid)

    @property
    def site(self):
        if self._site is None:
            self._site = settings.get_current_site()
        return self._site

    def itersites(self):
        for obj in self._cls.objects.all():
            default = '   *' if obj.is_default else ''
            yield obj.pk, obj.uid, obj.name, obj.fqdn, default

    def call_django_command(self, cmd, *args, **kwargs):
        return call_command(cmd, *args, **kwargs)

