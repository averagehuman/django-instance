
import os
import sys


def ensure_default_environ(fn):
    def wrapper(*args, **kwargs):
        os.environ.setdefault(
            'DJANGO_SETTINGS_MODULE',
            "instance.settings"
        )
        os.environ.setdefault(
            'DJANGO_APPLICATION_ROOT',
            os.getcwd(),
        )
        return fn(*args, **kwargs)
    return wrapper

@ensure_default_environ
def manage():
    from django.core import management
    from instance.conf import settings
    settings.configure()
    management.execute_from_command_line(sys.argv)

@ensure_default_environ
def serve():
    from instance.server import WSGIServer
    prog = "django-server"
    usage = "%s --settings=<DJANGO_SETTINGS_MODULE> [MORE OPTIONS}"
    WSGIServer(usage, prog).run()

@ensure_default_environ
def main(argv=sys.argv[1:]):
    from .application import UI
    from .manager import UIError
    ui = sys
    try:
        ui = UI()
        ui.run(argv)
    except KeyboardInterrupt:
        raise
    except Exception as e:
        ui.stderr.write("%s\n" % str(e))
        if '--debug' in argv:
            raise
        sys.exit(1)

