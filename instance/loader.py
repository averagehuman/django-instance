
from django.template.loaders.filesystem import Loader

from .utils import pathjoin, pathexists
from .conf import settings, SITE_STORAGE_ROOT_VARIABLE

class CurrentSiteLoader(Loader):
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        if not template_dirs:
            site_templates = pathjoin(
                settings[SITE_STORAGE_ROOT_VARIABLE], 'templates'
            )
            if pathexists(site_templates):
                template_dirs = [site_templates]
        return super(CurrentSiteLoader, self).load_template_source(
            template_name, template_dirs
        )

