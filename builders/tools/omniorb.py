"""omniorb build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack_bz2, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'lib','libomniORB4.so')):
        print('installing omniorb version',version)
        name = 'omniORB-'+str(version)+'.tar.bz2'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            t_url = 'https://sourceforge.net/projects/omniorb/files/omniORB/omniORB-' + str(version)
            url = os.path.join(t_url,name)
            wget(url,path)
            unpack_bz2(path,tmp_dir)
            oo_dir = os.path.join(tmp_dir,'omniORB-'+version)
            mod_env = dict(os.environ)
            mod_env['CFLAGS'] = '-fPIC'
            mod_env['CPPFLAGS'] = '-fPIC'
            if subprocess.call([os.path.join(oo_dir,'configure'),
                                '--prefix', dir_name,
                                '--bindir', dir_name+'/bin',
                                '--libdir', dir_name+'/lib',
                                '--includedir', dir_name+'/include',
                                '--datadir', dir_name+'/share',
                                '--enable-static', '--with-omniNames-logdir=/var/tmp',
                                '--without-openssl', '--disable-thread-tracing'],
                                cwd=oo_dir):
                raise Exception('omniorb failed to configure')
            if subprocess.call(['make'],cwd=oo_dir):
                raise Exception('omniorb failed to make')
            if subprocess.call(['make','install'],cwd=oo_dir):
                raise Exception('omni failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
