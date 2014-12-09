
import os

from django.utils.functional import LazyObject, empty


from .conf import settings

__version__ = '0.0.2'

__all__ = ['__version__', 'settings']

try:
    from elasticsearch import Elasticsearch
except ImportError:
    pass
else:
    class ES(LazyObject):

        def _setup(self):
            if self._wrapped is empty:
                self._wrapped = Elasticsearch(hosts=settings.get('ES_HOSTS'))

    es = ES()
    __all__.append('es')


