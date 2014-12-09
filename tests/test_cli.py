
import pytest

def test_application(ui):
    assert ui.parser.description == 'A Django CLI'
    with pytest.raises(SystemExit):
        ui.run(['-h'])
    assert ui.stdout.getvalue() == """\
usage: py.test [--version] [-v] [--log-file LOG_FILE] [-q] [-h] [--debug]
               [-H HOME] [--settings SETTINGS]

A Django CLI

optional arguments:
  --version             show program's version number and exit
  -v, --verbose         Increase verbosity of output. Can be repeated.
  --log-file LOG_FILE   Specify a file to log output. Disabled by default.
  -q, --quiet           suppress output except warnings and errors
  -h, --help            show this help message and exit
  --debug               show tracebacks on errors
  -H HOME, --home HOME  the application root directory, defaults to
                        $HOME/.django
  --settings SETTINGS   the DJANGO_SETTINGS_MODULE value

Commands:
  complete       print bash completion command
  help           print detailed help for another command
  sites          list all sites
"""


