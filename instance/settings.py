
from .defaults import *

INSTALLED_APPS += (
    'pipeline',
    'django_extensions',
)


import os
import musette

here = os.path.abspath(os.path.dirname(__file__))
cfgfile = os.path.join(here, '.config')

assert os.path.exists(cfgfile)

_cfg = {}

env = musette.Environment(
    _cfg,
    DEBUG=(bool, False),
)

env.read(cfgfile)

DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')

