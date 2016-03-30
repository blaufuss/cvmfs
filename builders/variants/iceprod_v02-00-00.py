# build the /iceprod/v02-00-00 directory, for this OS

import sys
import os
import subprocess
import tempfile
import shutil
import glob

from build_util import *

tools = get_tools()


def build(src,dest,**build_kwargs):
    """The main builder"""
    # first, make sure the base dir is there
    iceprod_version = 'v02-00-00'
    dir_name = os.path.join(dest,'iceprod',iceprod_version)
    copy_src(os.path.join(src,'iceprod',iceprod_version),dir_name)

    # now, do the OS-specific stuff
    load_env(dir_name)
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

    # reload env because ports is stupid
    load_env(os.path.join(dest,'iceprod',iceprod_version))

    tools['pip']['install']('futures==3.0.3')
    tools['pip']['install']('pycurl==7.21.5')
    tools['pip']['install']('setproctitle==1.1.9')

    tools['apsw']['3.9.2-r1'](dir_name)
