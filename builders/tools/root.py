"""root6 build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'bin','root')):
        print('installing root version',version)
        name = 'root_v'+str(version)+'.source.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('https://root.cern.ch/download/',name)
            wget(url,path)
            unpack(path,tmp_dir)
            root_dir = os.path.join(tmp_dir,'root-'+version)
            build_dir = os.path.join(tmp_dir,'build')
            os.mkdir(build_dir)
            if subprocess.call(['cmake',
                                '-Dgminimal=ON',
                                '-Dminuit2=ON',
                                '-Dgsl_shared=ON',
                                '-Dpythia6=ON',
                                '-Dpython=ON',
                                '-Dmathmore=ON',
                                '-Dx11=OFF',
                                '-Dasimage=ON',
                                '-DCMAKE_INSTALL_PREFIX='+dir_name,
                                root_dir],cwd=build_dir):
                raise Exception('root failed to cmake')
            if subprocess.call(['make'],cwd=build_dir):
                raise Exception('root failed to make')
            if subprocess.call(['make','install'],cwd=build_dir):
                raise Exception('root failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
