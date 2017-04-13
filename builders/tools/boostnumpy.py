"""boostnumpy build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None,old_boost=False):
    if not os.path.exists(os.path.join(dir_name,'lib','libboost_numpy.so')):
        print('installing boostnumpy version',version)
        if version=='master':
            name = 'master.tar.gz'
        else:
            name = 'V'+str(version)+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('https://github.com/martwo/BoostNumpy/archive/',name)
            wget(url,path)
            unpack(path,tmp_dir)
            boostnumpy_dir = os.path.join(tmp_dir,'BoostNumpy-'+version)
            build_dir = os.path.join(boostnumpy_dir,'build')
            if os.path.exists(build_dir):
                shutil.rmtree(build_dir)
            os.mkdir(build_dir)
            cmd = ['cmake','-DCMAKE_BUILD_TYPE=Release',
                   '-DCMAKE_INSTALL_PREFIX='+dir_name]
            if old_boost:
                cmd += ['-DBOOST_INCLUDEDIR='+os.path.join(os.environ['I3_PORTS'],'include','boost-1.38.0'),
                        '-DBOOST_LIBRARYDIR='+os.path.join(os.environ['I3_PORTS'],'lib','boost-1.38.0')]
            cmd += ['..']
            if subprocess.call(cmd,cwd=build_dir):
                raise Exception('boostnumpy failed to configure')
            if subprocess.call(['make'],cwd=build_dir):
                raise Exception('boostnumpy failed to make')
            if subprocess.call(['make','install'],cwd=build_dir):
                raise Exception('boostnumpy failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
