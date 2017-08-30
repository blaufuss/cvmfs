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

def build_instance(base_env, url, src, base_dir_name, debug=False, **ignored_args):
    # reset environ
    for k in list(os.environ):
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

    tag = os.path.basename(base_dir_name)
    if '.' in tag and os.path.exists(dir_name):
        print(tag+' already exists')
        return

    # fill OS-specific directory with dirs
    for d in ('bin','etc','include','lib','libexec','man',
              'share','tools','lib/python2.7/site-packages'):
        d = os.path.join(dir_name,d)
        if not os.path.exists(d):
            os.makedirs(d)
    # do symlinks
    for s,d in (('lib','lib64'),('bin','sbin')):
        d = os.path.join(dir_name,d)
        if not os.path.exists(d):
            os.symlink(os.path.join(dir_name,s),d)

    if '.' not in tag or LooseVersion(tag) >= LooseVersion('v2.3.0'):
        v2(dir_name, url, debug)
    else:
        v1(dir_name, url, debug)

    # make cvmfscatalog
    catalog = os.path.join(base_dir_name,'.cvmfscatalog')
    if not os.path.exists(catalog):
        with open(catalog,'a'):
            pass

def v1(dir_name, url, debug=False):
    """v1 - based on py2-v2"""
    tools['nginx']['1.9.9'](dir_name)
    tools['curl']['7.46.0'](dir_name)

    if os.environ['OS_ARCH'] == 'RHEL_6_x86_64':
        # we need gzip -k
        tools['gzip']['1.6'](dir_name)

    tools['apsw']['3.9.2-r1'](dir_name)

    if url.startswith('git+git'):
        tools['pip']['install'](url, dir_name, upgrade=True)
    else:
        tools['pip']['install'](url, dir_name)

def v2(dir_name, url, debug=False):
    """v2 - standalone. 2017-08-15"""
    # RHEL 6 is too old to build newer libtool
    if 'RHEL_6' in os.environ['OS_ARCH']:
        tools['libtool']['2.4.4'](dir_name)
    else:
        tools['libtool']['2.4.6'](dir_name)

    #tools['tcl_tk']['8.6.4'](dir_name)
    if os.environ['OS_ARCH'] == 'RHEL_6_x86_64':
        # we need gzip -k
        tools['gzip']['1.8'](dir_name)

    tools['bzip2']['1.0.6'](dir_name)

    tools['libffi']['3.2.1'](dir_name)
    tools['libxml2']['2.9.4'](dir_name)
    tools['sqlite']['3200000'](dir_name)
    tools['cmake']['3.2.2'](dir_name)

    tools['python']['3.6.2'](dir_name,pgo=not debug)
    tools['nginx']['1.13.4'](dir_name)
    tools['curl']['7.55.1'](dir_name)

    tools['apsw']['3.19.3-r1'](dir_name)

    if url.startswith('git+git'):
        tools['pip']['install'](url, dir_name, upgrade=True)
    else:
        tools['pip']['install'](url, dir_name)


def build(src,dest,version=None,**build_kwargs):
    """The main builder"""
    base_env = os.environ.copy()

    # get versions of iceprod
    releases = {}
    url = 'https://api.github.com/repos/WIPACrepo/iceprod/releases'
    f = urlopen(url)
    data = json.loads(f.read())
    f.close()
    for row in data:
        if not row['prerelease']:
            releases[row['tag_name']] = row['tarball_url']

    if version:
        releases = dict([(r,releases[r]) for r in releases if r == version])

    if (not version) or version not in releases:
        # build from git
        if not version:
            version = 'master'
        url = 'git+git://github.com/WIPACrepo/iceprod.git@'+version+'#egg=iceprod'
        base_dir_name = os.path.join(os.path.join(dest,'iceprod'),version)
        build_instance(base_env, url, src, base_dir_name, **build_kwargs)

    # build releases
    for tag in sorted(releases, key=LooseVersion):
        url = releases[tag]
        base_dir_name = os.path.join(os.path.join(dest,'iceprod'),tag)
        build_instance(base_env, url, src, base_dir_name, **build_kwargs)

    if not version:
        # add symlink to latest version
        sym_name = os.path.join(os.path.join(dest,'iceprod'), 'latest')
        if os.path.exists(sym_name):
            os.unlink(sym_name)
        os.symlink(base_dir_name, sym_name)
