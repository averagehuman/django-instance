
import os
import sys
import abc
import argparse

import six
import logbook
from termui import prompt

from cliff.command import Command
from cliff.lister import Lister

from instance.cli.application import CommandType
from instance.utils import pathjoin, pathexists, urlparse
from instance.conf import settings

log = logbook.Logger(__name__)


@six.add_metaclass(CommandType)
class Sites(Lister):
    """list all sites"""

    def take_action(self, args):
        return (
            ('ID', 'Name', 'Domain'),
            self.app.manager.itersites(),
        )

