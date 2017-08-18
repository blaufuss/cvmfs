"""zstd build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'bin','zstd')):
        print('installing zstd version',version)
        name = 'v'+str(version)+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('https://github.com/facebook/zstd/archive',name)
            wget(url,path)
            unpack(path,tmp_dir)
            zstd_dir = os.path.join(tmp_dir,'zstd-'+version)
            if subprocess.call(['make'],cwd=zstd_dir):
                raise Exception('zstd failed to make')
            if subprocess.call(['make','install','PREFIX='+dir_name],cwd=zstd_dir):
                raise Exception('zstd failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
