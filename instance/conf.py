# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import copy
import shutil

from django.utils.text import slugify
from django.utils.functional import LazyObject, empty
from django.core.management import call_command
from django.db import DEFAULT_DB_ALIAS

from .utils import (
    pathexists, pathjoin, dirname, mkdir, abspath, expanduser,
    text_type,
)

here = dirname(abspath(__file__))

DATA_ROOT_VARIABLE = "DJANGO_APPLICATION_ROOT"
DB_NAME_VARIABLE = "DJANGO_DATA_DB_NAME"
DB_PATH_VARIABLE = "DJANGO_DATA_DB_PATH"
SITE_UID_VARIABLE = "SITE_UID"
SITE_STORAGE_ROOT_VARIABLE = "SITE_STORAGE_ROOT"
DATA_DIR = '.django'
DEFAULT_DATA_ROOT = pathjoin(expanduser("~"), DATA_DIR)
DEFAULT_SITE_UID = "default"
DEFAULT_DB_NAME = "data.db"


def assert_configured(fn):
    def wrapper(self, *args, **kwargs):
        assert self._wrapped is not empty
        return fn(self, *args, **kwargs)
    return wrapper

class Environment(dict):

    __getattr__ = dict.__getitem__

    def __setattr__(self, key, val):
        self.__setitem__(key, val)

class Settings(LazyObject):

    def _setup(self):
        if self._wrapped is empty:
            self.configure()

    def configure(self, settings_module=None, overrides=None):
        """
        """
        if self._wrapped is not empty:
            raise RuntimeError('Settings already configured.')

        from django.conf import ENVIRONMENT_VARIABLE, settings as django_settings
        from django import setup
        from django.template.base import add_to_builtins

        if not django_settings.configured:
            settings_module = settings_module or 'instance.defaults'
            os.environ.setdefault(ENVIRONMENT_VARIABLE, settings_module)
            setup()
        add_to_builtins("instance.templatetags.loader_tags")

        env = django_settings._wrapped.__dict__
        if overrides:
            env.update(overrides)
        self._configure_defaults(env)
        self._configure_database(env)
        self._wrapped = Environment(env) #shallow copy
        self._site_cache = {}
        self.get_current_site()

    @property
    def configured(self):
        """
        Returns True if the settings have already been configured.
        """
        return self._wrapped is not empty

    def __getattr__(self, name):
        if self._wrapped is empty:
            self._setup()
        return getattr(self._wrapped, name)

    def __getitem__(self, name):
        if self._wrapped is empty:
            self._setup()
        return self._wrapped[name]

    def _configure_defaults(self, env):
        root = env.setdefault(
            DATA_ROOT_VARIABLE,
            os.environ.get(DATA_ROOT_VARIABLE, DEFAULT_DATA_ROOT)
        )
        siteid = env.setdefault(
            SITE_UID_VARIABLE,
            os.environ.get(SITE_UID_VARIABLE, DEFAULT_SITE_UID)
        )
        if not root:
            root = env[DATA_ROOT_VARIABLE] = DEFAULT_DATA_ROOT
        if not siteid:
            siteid = env[SITE_UID_VARIABLE] = DEFAULT_SITE_UID
        store = env.setdefault(
            SITE_STORAGE_ROOT_VARIABLE, pathjoin(root, 'sites', siteid)
        )
        if not env.get('SITE_NAME'):
            env['SITE_NAME'] = 'Django Site'
        if not env.get('SITE_TITLE'):
            env['SITE_TITLE'] = 'Django Site'
        if not env.get('SITE_SUBTITLE'):
            env['SITE_SUBTITLE'] = ''
        if not env.get('SITE_DESCRIPTION'):
            env['SITE_DESCRIPTION'] = ''
        if not env.get('SITE_DOMAIN'):
            env['SITE_DOMAIN'] = 'http://127.0.0.1:8000'
        if not env.get('MEDIA_ROOT'):
            env['MEDIA_ROOT'] = pathjoin(store, 'media')
        if not env.get('STATIC_ROOT'):
            env['STATIC_ROOT'] = pathjoin(store, 'assets')
        if not env.get('MEDIA_URL'):
            env['MEDIA_URL'] = '/media/'
        if not env.get('STATIC_URL'):
            env['STATIC_URL'] = '/assets/'
        dbname = env.get(DB_NAME_VARIABLE, DEFAULT_DB_NAME)
        env.setdefault(DB_PATH_VARIABLE, pathjoin(root, dbname))
        mkdir(store)
        mkdir(pathjoin(store, 'static'))
        mkdir(pathjoin(store, 'templates'))
        mkdir(env["STATIC_ROOT"])
        mkdir(env["MEDIA_ROOT"])

    def _configure_database(self, env):
        """Create sites database if it doesn't exist"""
        db_settings = env.get('DATABASES')
        if db_settings:
            #assume database already exists and is synced
            return
        db_path = env[DB_PATH_VARIABLE]
        mkdir(dirname(db_path))
        db_settings = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': db_path
        }
        env['DATABASES'] = {
            'default': db_settings,
        }
        # if DATABASES is {} then there may already be a dummy connection at
        # this point
        from django.db import connections
        try:
            del connections['default']
        except:
            pass
        connections.databases['default'] = db_settings
        if not pathexists(db_path):
            call_command('migrate', interactive=False)

    def _create_or_update_site(self, uid, env):
        from instance.models import DjangoSite
        created = False
        try:
            site = DjangoSite.objects.get(
                uid__iexact=env[SITE_UID_VARIABLE]
            )
        except DjangoSite.DoesNotExist:
            site = DjangoSite(uid=env[SITE_UID_VARIABLE])
            created = True
        site.name = env['SITE_NAME']
        site.title = env['SITE_TITLE']
        site.subtitle = env['SITE_SUBTITLE']
        site.description = env['SITE_DESCRIPTION']
        site.fqdn = env['SITE_DOMAIN']
        site.save()
        self.init_site(site)
        return site
        
    @assert_configured
    def get_current_site(self):
        env = self._wrapped
        try:
            uid = slugify(text_type(env[SITE_UID_VARIABLE]))
        except KeyError:
            raise ImproperlyConfigured(
                "Missing %s setting" % SITE_UID_VARIABLE
            )
        try:
            return self._site_cache[uid]
        except KeyError:
            pass
        site = self._site_cache[uid] = self._create_or_update_site(uid, env)
        return site

    def init_site(self, site):
        home = settings[SITE_STORAGE_ROOT_VARIABLE]
        site_template_dir = pathjoin(home, 'templates')
        mkdir(home)
        mkdir(site_template_dir)
        # create site-specfic css file
        styles = pathjoin(home, 'static', 'site.css')
        if not pathexists(styles):
            mkdir(dirname(styles))
            with open(styles, 'w') as f:
                f.write("/* site-specific styles */\n")
        # site long description from README
        for fname in ['README', 'README.md']:
            infofile = pathjoin(home, fname)
            if pathexists(infofile):
                break
        else:
            infofile = None
        if infofile:
            try:
                from markdown import markdown
            except ImportError:
                return
            with open(infofile, 'rb') as fd:
                text = fd.read()
            try:
                html = markdown(text)
            except:
                html = text
            if site.info != html:
                site.info = html
                site.save()

settings = Settings()

