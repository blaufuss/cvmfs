"""hiredis build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'lib/','libhiredis.so')):
        print('hiredis version',version)
        name = 'v'+version+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            t_url = 'https://github.com/redis/hiredis/archive/'
            url = os.path.join(t_url,name)
            wget(url,path)
            unpack(path,tmp_dir)
            oo_dir = os.path.join(tmp_dir,'hiredis-'+version)
            mod_env = dict(os.environ)
            if subprocess.call(['make'],cwd=oo_dir):
                raise Exception('hiredis failed to make')
            if subprocess.call(['make','PREFIX='+dir_name,'install'],cwd=oo_dir):
                raise Exception('hiredis failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
