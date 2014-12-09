
import os

from django.core.files.storage import FileSystemStorage
from django.contrib.staticfiles.finders import BaseStorageFinder
from django.utils.functional import LazyObject

from .utils import pathjoin, pathexists
from .conf import settings, SITE_STORAGE_ROOT_VARIABLE

class CurrentSiteStorage(LazyObject):
    def _setup(self):
        self._wrapped = FileSystemStorage(
            pathjoin(settings[SITE_STORAGE_ROOT_VARIABLE], 'static')
        )

class CurrentSiteStaticFinder(BaseStorageFinder):

    storage = CurrentSiteStorage()



