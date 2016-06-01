"""gcc build/install"""

import os
import subprocess
import tempfile
import shutil
import copy

from build_util import wget, unpack, version_dict

try:
    import multiprocessing
    cpu_cores = multiprocessing.cpu_count()
except ImportError:
    cpu_cores = 1

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'bin','gfortran')):
        print('installing gcc version',version,'(gfortran only)')
        name = 'gcc-'+str(version)+'.tar.gz'

        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('https://ftp.gnu.org/gnu/gcc/gcc-'+str(version),name)
            wget(url,path)
            unpack(path,tmp_dir)
            gcc_dir = os.path.join(tmp_dir,'gcc-'+version)

            # this line does not seem to work correctly - it will still compile and install a g++ and libstdc++
            languages = 'c,fortran'

            configure_options = [
                '--prefix='+dir_name,
                '--enable-languages='+languages,
                '--with-gmp='+dir_name,
                '--with-mpfr='+dir_name,
                '--with-mpc='+dir_name,
                '--with-isl='+dir_name,
                '--disable-multilib',
            ]

            configure_options+=['--disable-build-poststage1-with-cxx']

            if subprocess.call([os.path.join(gcc_dir,'configure')]+configure_options,
                                cwd=gcc_dir):
                raise Exception('gcc failed to configure')

            mod_env = copy.deepcopy(os.environ)
            mod_env['LD_LIBRARY_PATH'] = os.path.join(dir_name,'lib')
            if subprocess.call(['make','-j'+str(cpu_cores)],cwd=gcc_dir,env=mod_env):
                raise Exception('gcc failed to make')
            # TODO: maybe install into a temporary DESTDIR, get rid of the gcc and g++ parts and only then move to the actual installation prefix
            if subprocess.call(['make','install'],cwd=gcc_dir,env=mod_env):
                raise Exception('gcc failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
