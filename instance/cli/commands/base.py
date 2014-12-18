
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
from instance.cli.controller import UIError
from instance.utils import pathjoin, pathexists, text_type, urlparse
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
            help="a name or unique id for the site",
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
            help="don't prompt user for unspecified parameters",
        )
        return parser

    def take_action(self, args):
        name = args.site
        if not name:
            if not args.interactive:
                raise UIError("required argument 'site'")
            name = prompt("Enter a name for the Site")
        uid = args.uid or slugify(text_type(name))
        fqdn = args.fqdn or "127.0.0.1:8000"
        title = args.title or name
        if args.interactive and not self.app.ctl.exists(uid):
            if not args.uid:
                uid = prompt(
                    "Enter a unique identifier for the Site",
                    default=uid,
                )
            if uid != slugify(text_type(uid)):
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
        self.app.ctl.init_site(uid, name, fqdn, title)

@six.add_metaclass(CommandType)
class Ls(Lister):
    """list all sites"""

    def take_action(self, args):
        return (
            ('PK', 'ID', 'Name', 'Domain', 'Default'),
            self.app.ctl.itersites(),
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
            help="the unique identifier (slug or pk) of the site to delete",
        )
        return parser

    def take_action(self, args):
        self.app.ctl.remove_site(args.uid)

