"""zthread build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'lib','libZThread.so')):
        print('installing zthread.  Fixed  version 2.3.2_IceCube')
        name = 'ZThread-2.3.2-patchedi3.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            t_url = 'http://code.icecube.wisc.edu/tools/distfiles/zthread'
            url = os.path.join(t_url,name)
            wget(url,path)
            unpack(path,tmp_dir)
            oo_dir = os.path.join(tmp_dir,'ZThread-2.3.2')
            mod_env = dict(os.environ)
            mod_env['CFLAGS'] = '-fPIC'
            mod_env['CPPFLAGS'] = '-fPIC'
            if subprocess.call([os.path.join(oo_dir,'configure'),
                                '--prefix', dir_name,
                                '--bindir', dir_name+'/bin/zthread-2.3.2',
                                '--includedir', dir_name+'/include/zthread-2.3.2',
                                '--datadir', dir_name+'/share/zthread-2.3.2',
                                '--enable-shared', '--enable-static'],
                                cwd=oo_dir):
                raise Exception('zthread failed to configure')
            if subprocess.call(['make'],cwd=oo_dir):
                raise Exception('zthread failed to make')
            if subprocess.call(['make','install'],cwd=oo_dir):
                raise Exception('zthread failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
