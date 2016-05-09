# build the /iceprod directory, for this OS

import sys
import os
import subprocess
import tempfile
import shutil
import glob
import json
from distutils.version import LooseVersion

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

from build_util import *

tools = get_tools()


def build(src,dest,**build_kwargs):
    """The main builder"""
    base_env = os.environ.copy()

    # get versions of iceprod
    releases = {}
    url = 'https://api.github.com/repos/WIPACrepo/iceprod/releases'
    with urlopen(url) as f:
        data = json.loads(f.read())
        for row in data:
            releases[row['tag_name']] = row['tarball_url']

    for tag in sorted(releases, key=LooseVersion):
        url = releases[tag]
        base_dir_name = os.path.join(os.path.join(dest,'iceprod'),tag)

        # reset environ
        for k in os.environ:
            del os.environ[k]
        for k in base_env:
            os.environ[k] = base_env[k]

        # first, make sure the static content is there
        copy_src(os.path.join(src,'iceprod','all'), base_dir_name)
        
        # now, do the OS-specific stuff
        load_env(base_dir_name)
        if 'ICEPRODROOT' not in os.environ:
            raise Exception('$ICEPRODROOT not defined')
        dir_name = os.environ['ICEPRODROOT']

        # fill OS-specific directory with dirs
        for d in ('bin','etc','include','lib','libexec','man',
                  'share','tools'):
            d = os.path.join(dir_name,d)
            if not os.path.exists(d):
                os.makedirs(d)
        # do symlinks
        for src,dest in (('lib','lib64'),('bin','sbin')):
            dest = os.path.join(dir_name,dest)
            if not os.path.exists(dest):
                os.symlink(os.path.join(dir_name,src),dest)

        tools['nginx']['1.9.9'](dir_name)
        tools['curl']['7.46.0'](dir_name)

        if os.environ['OS_ARCH'] == 'RHEL_6_x86_64':
            # we need gzip -k
            tools['gzip']['1.6'](dir_name)

        # reload env because ports is stupid
        load_env(base_dir_name)

        tools['pip']['install']('futures==3.0.3', dir_name)
        tools['pip']['install']('pycurl==7.21.5', dir_name)
        tools['pip']['install']('setproctitle==1.1.9', dir_name)

        tools['apsw']['3.9.2-r1'](dir_name)

        # install iceprod
        tools['pip']['install'](url, dir_name)

    # add symlink to latest version
    sym_name = os.path.join(os.path.join(dest,'iceprod'), 'current')
    if os.path.exists(sym_name):
        os.unlink(sym_name)
    os.symlink(sym_name, base_dir_name)
