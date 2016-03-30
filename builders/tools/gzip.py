"""gzip build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'bin','gzip')):
        print('installing gzip version',version)
        name = 'gzip-'+str(version)+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('http://ftp.gnu.org/gnu/gzip',name)
            wget(url,path)
            unpack(path,tmp_dir)
            gzip_dir = os.path.join(tmp_dir,'gzip-'+version)
            if subprocess.call([os.path.join(gzip_dir,'configure'),
                                '--prefix',dir_name],cwd=gzip_dir):
                raise Exception('gzip failed to configure')
            if subprocess.call(['make'],cwd=gzip_dir):
                raise Exception('gzip failed to make')
            if subprocess.call(['make','install'],cwd=gzip_dir):
                raise Exception('gzip failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
