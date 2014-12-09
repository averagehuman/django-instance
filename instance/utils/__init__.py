
from .path import pathjoin, pathexists, normpath, realpath, expanduser
from .path import dirname, basename, abspath, splitext, relpath
from .path import iterfiles, mkdir, ensure_parent_dir, ensure_relpath
from .path import copytree, INVALID_GLOB
from .compat import urlparse, text_type, bytes, basestring, BytesIO

def import_object(name):
    """Imports an object by name.

    import_object('x.y.z') is equivalent to 'from x.y import z'.

    """
    name = str(name)
    if '.' not in name:
        return __import__(name)
    parts = name.split('.')
    m = '.'.join(parts[:-1])
    attr = parts[-1]
    obj = __import__(m, None, None, [attr], 0)
    try:
        return getattr(obj, attr)
    except AttributeError as e:
        raise ImportError("'%s' does not exist in module '%s'" % (attr, m))

