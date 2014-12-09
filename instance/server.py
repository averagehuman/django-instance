
from django.core.handlers.wsgi import WSGIHandler

import gunicorn.app.base
import gunicorn.config

from .conf import settings, DATA_ROOT_VARIABLE
from .utils import urlparse

# Subclassing 'Setting' makes  gunicorn arg parser aware of additional
# command line options
class Home(gunicorn.config.Setting):
    name = "home"
    section = "Django"
    cli = ["-H", "--home"]
    meta = "DIR"
    validator = gunicorn.config.validate_file
    default = None
    desc = """\
        The DJANGO_APPLICATION_ROOT directory
    """

class WSGIServer(gunicorn.app.base.Application):
    
    def load_default_config(self):
        # init configuration
        self.cfg = gunicorn.config.Config(
            usage=self.usage, prog=self.prog
        )

    def init(self, parser, options, args):
        overrides = {}
        if options.home:
            overrides[DATA_ROOT_VARIABLE] = options.home
        if options.debug:
            overrides['DEBUG'] = True
        django_settings = options.django_settings or \
                self.cfg.env.get("DJANGO_SETTINGS_MODULE")
        settings.configure(django_settings, overrides)
        self.cfg.set("default_proc_name", settings.SITE_UID)

    def get_media_root_and_prefix(self):
        url = settings.MEDIA_URL
        root = settings.MEDIA_ROOT
        prefix = urlparse(url).path
        prefix = '/{}/'.format(prefix.strip('/'))
        return root, prefix

    def load(self):
        handler = WSGIHandler()
        try:
            from whitenoise.django import DjangoWhiteNoise
        except ImportError:
            pass
        else:
            handler = DjangoWhiteNoise(handler)
            media_root, media_prefix = self.get_media_root_and_prefix()
            handler.add_files(media_root, prefix=media_prefix)
        return handler

