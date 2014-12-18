
import os
import sys
import abc
import argparse

import six
import logbook
from termui import prompt

from django.utils.text import slugify

from cliff.command import Command
from cliff.lister import Lister

from instance.cli.application import CommandType
from instance.cli.manager import UIError
from instance.utils import pathjoin, pathexists, urlparse
from instance.conf import settings

log = logbook.Logger(__name__)


@six.add_metaclass(CommandType)
class Init(Command):
    """initialise a new site"""

    def get_parser(self, *args, **kwargs):
        parser = super(Init, self).get_parser(*args, **kwargs)
        parser.add_argument(
            'site',
            action='store',
            nargs='?',
            default=None,
            help="the name of the site to serve",
        )
        parser.add_argument(
            '--uid',
            action='store',
            default=None,
            help="the unique id of the new site (default: slugified name)",
        )
        parser.add_argument(
            '--fqdn',
            action='store',
            default=None,
            help="the domain name of the site (default: 127.0.0.1:8000)"
        )
        parser.add_argument(
            '--title',
            action='store',
            default=None,
            help="the display title of the new site",
        )
        parser.add_argument(
            '--noinput',
            action='store_false',
            dest='interactive',
            default=True,
            help="prompt user for unspecified site data",
        )
        parser.add_argument(
            '-i', '--ignore-existing',
            action='store_false',
            dest='strict',
            default=True,
            help="do nothing if a site with this name exists",
        )
        return parser

    def take_action(self, args):
        name = args.site
        if not name:
            if not args.interactive:
                raise UIError("required argument 'site'")
            name = prompt("Enter a name for the Site")
        uid = args.uid or slugify(name)
        fqdn = args.fqdn or "127.0.0.1:8000"
        title = args.title or name
        if args.interactive:
            if not args.uid:
                uid = prompt(
                    "Enter a unique identifier for the Site",
                    default=uid,
                )
            if uid != slugify(uid):
                raise UIError("invalid identifier '%s'" % uid)
            if not args.fqdn:
                fqdn = prompt(
                    "Enter a domain for the Site",
                    default=fqdn,
                )
            if not args.title:
                title = prompt(
                    "Enter a display title for the Site",
                    default=title,
                )
        self.app.manager.init_site(uid, name, fqdn, title, args.strict)

@six.add_metaclass(CommandType)
class Ls(Lister):
    """list all sites"""

    def take_action(self, args):
        return (
            ('ID', 'Name', 'Domain'),
            self.app.manager.itersites(),
        )

@six.add_metaclass(CommandType)
class Rm(Command):
    """delete a site"""

    def get_parser(self, *args, **kwargs):
        parser = super(Rm, self).get_parser(*args, **kwargs)
        parser.add_argument(
            'uid',
            action='store',
            default=None,
            help="the unique identifier (slug) of the site to delete",
        )
        return parser

    def take_action(self, args):
        self.app.manager.remove_site(args.uid)

