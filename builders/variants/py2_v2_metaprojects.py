# build the /py2-v1 directory, for this OS

import sys
import os
import subprocess
import tempfile
import shutil

from build_util import *

tools = get_tools()

def build(src,dest,svn_up=None,**build_kwargs):
    """The main builder"""
    # first, make sure the base dir is there
    dir_name = os.path.join(dest,'py2-v2')
    if not os.path.isdir(dir_name):
        raise Exception('base does not exist')
    
    # now, do the OS-specific stuff
    load_env(dir_name)
    if 'SROOT' not in os.environ:
        raise Exception('$SROOT not defined')
    dir_name = os.environ['SROOT']
    
    kwargs = {}
    if svn_up is not None:
        kwargs['svn_up'] = svn_up

    # releases
    tools['i3_metaproject']['offline-software']['V15-08-00'](dir_name,**kwargs)
    tools['i3_metaproject']['simulation']['V05-00-00'](dir_name,**kwargs)
    tools['i3_metaproject']['icerec']['V05-00-00'](dir_name,**kwargs)

    # trunks
    tools['i3_metaproject']['combo']['stable'](dir_name,**kwargs)
    #tools['i3_metaproject']['offline-software']['trunk'](dir_name,**kwargs)
    #tools['i3_metaproject']['simulation']['trunk'](dir_name,**kwargs)
    #tools['i3_metaproject']['icerec']['trunk'](dir_name,**kwargs)
    #tools['i3_metaproject']['combo']['trunk'](dir_name,**kwargs)

