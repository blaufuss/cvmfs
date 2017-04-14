"""nlopt build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict, cpu_cores

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'lib','libnlopt_cxx.so')):
        print('installing nlopt version',version)
        name = 'nlopt-'+str(version)+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('http://ab-initio.mit.edu/nlopt',name)
            wget(url,path)
            unpack(path,tmp_dir)
            nlopt_dir = os.path.join(tmp_dir,'nlopt-'+version)
            options = [
                '--enable-shared',
                '--with-cxx',
                '--without-guile',
                '--without-octave',
                '--without-matlab',
            ]
            if subprocess.call([os.path.join(nlopt_dir,'configure'),
                                '--prefix',dir_name]+options,
                                cwd=nlopt_dir):
                raise Exception('nlopt failed to configure')
            if subprocess.call(['make', '-j', cpu_cores],cwd=nlopt_dir):
                raise Exception('nlopt failed to make')
            if subprocess.call(['make','install'],cwd=nlopt_dir):
                raise Exception('nlopt failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
