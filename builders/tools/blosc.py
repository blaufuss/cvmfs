"""blosc build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'lib','libblosc.so')):
        print('installing blosc version',version)
        name = 'v'+str(version)+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('https://github.com/Blosc/c-blosc/archive',name)
            wget(url,path)
            unpack(path,tmp_dir)
            blosc_dir = os.path.join(tmp_dir,'c-blosc-'+version)
            build_dir = os.path.join(tmp_dir,'build')
            os.mkdir(build_dir)
            if subprocess.call(['cmake','-DCMAKE_INSTALL_PREFIX='+dir_name,
                                '-DPREFER_EXTERNAL_ZSTD=ON',
                                blosc_dir],cwd=build_dir):
                raise Exception('blosc failed to make')
            if subprocess.call(['make'],cwd=build_dir):
                raise Exception('blosc failed to make')
            if subprocess.call(['make','install'],cwd=build_dir):
                raise Exception('blosc failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
