

import os
import sys
import abc
import argparse

import six

from cliff.command import Command
from cliff.lister import Lister

from instance.cli.application import CommandType
from instance.utils import pathjoin, pathexists
from instance.cli.manager import UIError

import cli53

class BaseZoneCommand(Command):

    @property
    def route53(self):
        try:
            conn = self._route53
        except AttributeError:
            conn = self._route53 = cli53.get_route53_connection()
        return conn

@six.add_metaclass(CommandType)
class Create(BaseZoneCommand):
    """create a new Route53 Zone"""

    def get_parser(self, *args, **kwargs):
        parser = super(Create, self).get_parser(*args, **kwargs)
        parser.add_argument(
            'zone',
            help= 'zone name',
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            default=False,
            help='wait for changes to become live (default: false)'
        )
        parser.add_argument(
            '--comment',
            help='add a comment to the zone'
        )
        return parser

    def take_action(self, args):
        cli53.cmd_create(args, self.route53)


