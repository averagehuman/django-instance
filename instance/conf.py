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
DEFAULT_DATA_ROOT = os.getcwd()#pathjoin(os.getcwd(), DATA_DIR)
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
        self._configure_data_root(env)
        self._configure_database(env)
        self._configure_defaults(env)
        self._wrapped = Environment(env) #shallow copy
        self._site_cache = {}
        #self.get_current_site()

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

    def _configure_data_root(self, env):
        root = env.setdefault(
            DATA_ROOT_VARIABLE,
            os.environ.get(DATA_ROOT_VARIABLE, DEFAULT_DATA_ROOT)
        )
        if not root:
            root = env[DATA_ROOT_VARIABLE] = DEFAULT_DATA_ROOT

    def _configure_database(self, env):
        """Create sites database if it doesn't exist"""
        db_settings = env.get('DATABASES')
        if db_settings:
            #assume database already exists and is synced
            return
        root = env[DATA_ROOT_VARIABLE]
        dbname = env.get(DB_NAME_VARIABLE, DEFAULT_DB_NAME)
        db_path = env.setdefault(DB_PATH_VARIABLE, pathjoin(root, dbname))
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

    def _configure_defaults(self, env):
        siteid = os.environ.get(SITE_UID_VARIABLE)
        siteid = siteid or env.get(SITE_UID_VARIABLE)
        if not siteid:
            from instance.models import DjangoSite
            site = DjangoSite.objects.get_default()
            siteid = site.uid
        siteid = env[SITE_UID_VARIABLE] = siteid or DEFAULT_SITE_UID
        root = env[DATA_ROOT_VARIABLE]
        store = env.setdefault(
            SITE_STORAGE_ROOT_VARIABLE, pathjoin(root, siteid)
        )
        if not env.get('MEDIA_ROOT'):
            env['MEDIA_ROOT'] = pathjoin(store, 'media')
        if not env.get('STATIC_ROOT'):
            env['STATIC_ROOT'] = pathjoin(store, 'assets')
        if not env.get('MEDIA_URL'):
            env['MEDIA_URL'] = '/media/'
        if not env.get('STATIC_URL'):
            env['STATIC_URL'] = '/assets/'
        mkdir(store)
        mkdir(pathjoin(store, 'static'))
        mkdir(pathjoin(store, 'templates'))
        mkdir(env["STATIC_ROOT"])
        mkdir(env["MEDIA_ROOT"])

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
            site = self._site_cache[uid]
        except KeyError:
            site = self._site_cache[uid] = DjangoSite.objects.get(
                uid__iexact=env[SITE_UID_VARIABLE]
            )
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

