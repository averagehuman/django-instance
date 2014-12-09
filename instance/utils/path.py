
import os
from fnmatch import fnmatch
import shutil

from .compat import ExitStack

pathjoin = os.path.join
pathexists = os.path.exists
normpath = os.path.normpath
expanduser = os.path.expanduser
abspath = os.path.abspath
dirname = os.path.dirname
basename = os.path.basename
splitext = os.path.splitext
relpath = os.path.relpath

IGNORE_EXT = set([
    '.swp', '.log', '~', '.pyc', '.pyo', '.pyd', '.conf', '.cfg',
])
IGNORE_DIRS = set([
    '.git', '.hg', '.svn', '.bzr', '.tox', 'templates',
])
VALID_EXT = set([
    '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.ico',
    '.pdf', '.doc', '.docx', '.ppt', '.xls',
    '.txt', '.rst',
    '.md', '.markdown',
    '.html', '.css',
])
VALID_GLOB = set(['*'+ext for ext in VALID_EXT])
INVALID_GLOB = ['*'+ext for ext in IGNORE_EXT] + list(IGNORE_DIRS)

def copytree(src, dst):
    return shutil.copytree(
        src, dst, ignore=shutil.ignore_patterns(*INVALID_GLOB)
    )

def realpath(fpath):
    return os.path.realpath(normpath(fpath))

def filtered(filenames, glob=None):
    glob = glob or VALID_GLOB
    for f in filenames:
        if not f or f[-1:] == '~' or splitext(f)[1].lower() in IGNORE_EXT:
            continue
        for pattern in glob:
            if fnmatch(f, pattern):
                yield f
                break

def iterfiles(source, root='', glob=None, ignore=None):
    source = realpath(pathjoin(source, root))
    depth = len([d for d in source.split(os.sep) if d])
    if ignore is None:
        ignore= IGNORE_DIRS
    def skip(d):
        return d.lower().strip(os.sep) in ignore
    for top, dirs, files in os.walk(source):
        dirs[:] = sorted([d for d in dirs if not skip(d)])
        relroot = os.sep.join(top.split(os.sep)[depth+1:])
        for fname in sorted(filtered(files, glob)):
            srcpath = os.path.join(top, fname)
            relpath = os.path.join(relroot, fname)
            yield fname, relpath, srcpath

def iteropen(source, root='', glob=None, ignore=None):
    with ExitStack() as stack:
        for fname, relpath, srcpath in iterfiles(source, root, glob, ignore):
            yield fname, relpath, stack.enter_context(open(srcpath))

def mkdir(path):
    """If a directory does not exist, create it and any parent directory

    If 'path' exists and is a directory, do nothing, otherwise fail.
    """
    if not pathexists(path):
        os.makedirs(path)
    elif not os.path.isdir(path):
        raise OSError("'%s' exists and is not a directory")

def ensure_parent_dir(path):
    parent = dirname(path)
    mkdir(parent)
    return parent

def ensure_relpath(path):
    if path is None:
        return ''
    return path.strip().strip('./\\').strip()


