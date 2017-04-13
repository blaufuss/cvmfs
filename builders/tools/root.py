"""root6 build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None,x11=False):
    if not (os.path.exists(os.path.join(dir_name,'bin','root'))
         or os.path.exists(os.path.join(dir_name,'bin','root.exe'))):
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
            options = [
                    '-Dgminimal=ON',
                    '-Dminuit2=ON',
                    '-Dgsl_shared=ON',
                    '-Dpythia6=ON',
                    '-Dpython=ON',
                    '-Dmathmore=ON',
                    '-Dasimage=ON',
            ]
            if x11:
                options.append('-Dx11=ON')
            else:
                options.append('-Dx11=OFF')
            if subprocess.call(['cmake']+options+[
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
    # need 6.10 or better
    def bad(v):
        return any(v.startswith(k) for k in ('5.','6.00','6.02','6.04','6.06','6.08'))
    return version_dict(install, bad_versions=bad)
