
import os
import sys
import abc
import inspect
import shlex

import logbook
from logbook.more import ColorizedStderrHandler

from cliff.app import App
from cliff.commandmanager import CommandManager, EntryPointWrapper

try:
    import cli53
    HAS_CLI53 = True
except:
    HAS_CLI53 = False

from instance import __version__
from instance.utils import import_object, pathjoin, expanduser
from instance.conf import settings, DATA_ROOT_VARIABLE, DB_PATH_VARIABLE
from .manager import CurrentSiteManager

registry = {}

class CommandType(abc.ABCMeta):
    """Metaclass for all Command classes in 'instance.cli.commands'
    
    A poor man's discovery mechanism - Command classes of this type will
    register themselves in the global registry whenever the modules in which
    they live are imported. The registry key will be the lowercased name of the
    class or, in the case of submodules, the name of the class prefixed with the 
    module name.
    Eg. 'instance.cli.commands.Serve' -> 'serve'
        'instance.cli.commands.zones.Create' -> 'zones create'
    """

    root = 'instance.cli.commands.'
    def __new__(cls, name, bases, attrs):
        prefix = attrs['__module__'].partition(cls.root)[2].split('.')
        if prefix and prefix[-1] == 'base':
            prefix = prefix[:-1]
        prefix = ' '.join(prefix)
        prefix = prefix and prefix + ' '
        key = prefix + name.lower()
        t = abc.ABCMeta.__new__(cls, name, bases, attrs)
        registry[key] = EntryPointWrapper(name.lower(), t)
        return t

    @classmethod
    def import_module(cls, name=None):
        if not name:
            module = cls.root.rstrip('.')
        else:
            module = cls.root + name
        import_object(module)

class UICommandManager(CommandManager):

    def load_commands(self, namespace):
        CommandType.import_module('base')
        if HAS_CLI53:
            CommandType.import_module('zones')
        self.commands.update(registry)

class UI(App):
    NAME = "instance"
    LOG = logbook.Logger("instance.cli")

    def __init__(self, *args, **kwargs):
        kwargs.update(dict(
            description='A Django CLI',
            version=__version__,
            command_manager=UICommandManager('instance.cli'),
            )
        )
        super(UI, self).__init__(*args, **kwargs)
        self._manager = None

    def build_option_parser(self, *args, **kwargs):
        parser = super(UI, self).build_option_parser(*args, **kwargs)
        parser.add_argument(
            '-H', '--home',
            action='store',
            default=None,
            help="the application root directory, defaults to $PWD/.django",
        )
        parser.add_argument(
            '--settings',
            action='store',
            default=None,
            help="if not already set, the DJANGO_SETTINGS_MODULE environment"
            " variable will be set to this value",
        )
        return parser

    @property
    def manager(self):
        if self._manager is None:
            self._manager = CurrentSiteManager()
        return self._manager

    def initialize_app(self, argv):
        overrides = {}
        if self.options.home:
            overrides[DATA_ROOT_VARIABLE] = self.options.home
        if self.options.debug:
            overrides['DEBUG'] = True
        settings.configure(self.options.settings, overrides)
        self.settings = self.options.settings

    def run(self, argv):
        handler = ColorizedStderrHandler(bubble=False)
        with handler:
            return super(UI, self).run(argv)

    def interact(self):
        return self.run(['-h'])

