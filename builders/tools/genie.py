"""geant4 build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None,data_dir=None):
    if not os.path.exists(os.path.join(dir_name,'bin','geant4')):
        print('installing geant4 version',version)
        name = 'v'+str(version)+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('https://github.com/Geant4/geant4/archive',name)
            wget(url,path)
            unpack(path,tmp_dir)
            geant4_dir = os.path.join(tmp_dir,'geant4-'+version)
            build_dir = os.path.join(tmp_dir,'build')
            os.mkdir(build_dir)
            options = ['-DGEANT4_INSTALL_DATA=ON',
                       '-DCMAKE_BUILD_TYPE=Release',
                      ]
            if data_dir:
                options.append('-DGEANT4_INSTALL_DATADIR='+data_dir)
            if subprocess.call(['cmake',
                                '-DCMAKE_INSTALL_PREFIX='+dir_name]
                                +options+[geant4_dir],cwd=build_dir):
                raise Exception('geant4 failed to cmake')
            if subprocess.call(['make'],cwd=build_dir):
                raise Exception('geant4 failed to make')
            if subprocess.call(['make','install'],cwd=build_dir):
                raise Exception('geant4 failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
