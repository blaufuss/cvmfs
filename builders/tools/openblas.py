"""openblas build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict, get_fortran_compiler, cpu_cores

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'lib','libopenblas.so')):
        print('installing openblas version',version)
        name = 'v'+version+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('https://github.com/xianyi/OpenBLAS/archive',name)
            wget(url,path)
            unpack(path,tmp_dir)
            openblas_dir = os.path.join(tmp_dir,'OpenBLAS-'+version)
            makefile = os.path.join(openblas_dir,'Makefile.rule')
            with open(makefile,'a') as f:
                f.write('DYNAMIC_ARCH = 1\n')
                f.write('NO_AVX2 = 1\n')
                f.write('PREFIX = %s\n'%dir_name)
                f.write('NUM_THREADS = 24\n')
            if subprocess.call(['make', '-j', cpu_cores],cwd=openblas_dir):
                raise Exception('openblas failed to make')
            if subprocess.call(['make','install'],cwd=openblas_dir):
                raise Exception('openblas failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
