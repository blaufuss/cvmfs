"""photospline build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict, cpu_cores

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'lib','libcphotospline.so')):
        print('installing photospline version',version)
        if version=='master':
            name = 'master.tar.gz'
        else:
            name = 'v'+str(version)+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('https://github.com/cnweaver/photospline/archive/',name)
            wget(url,path)
            unpack(path,tmp_dir)
            photospline_dir = os.path.join(tmp_dir,'photospline-'+version)
            build_dir = os.path.join(photospline_dir,'build')
            if os.path.exists(build_dir):
                shutil.rmtree(build_dir)
            os.mkdir(build_dir)
            cmd = ['cmake','-DCMAKE_BUILD_TYPE=Release',
                   '-DCMAKE_INSTALL_PREFIX='+dir_name]
            cmd += ['..']
            if subprocess.call(cmd,cwd=build_dir):
                raise Exception('photospline failed to configure')
            if subprocess.call(['make','-j',cpu_cores],cwd=build_dir):
                raise Exception('photospline failed to make')
            if subprocess.call(['make','install'],cwd=build_dir):
                raise Exception('photospline failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
