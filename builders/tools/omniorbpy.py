"""omniorbpy build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack_bz2, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'lib/python2.7/site-packages/omniORB','CORBA.py')):
        print('installing omniorbpy version',version)
        name = 'omniORBpy-'+str(version)+'.tar.bz2'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            t_url = 'https://sourceforge.net/projects/omniorb/files/omniORBpy/omniORBpy-' + str(version)
            url = os.path.join(t_url,name)
            wget(url,path)
            unpack_bz2(path,tmp_dir)
            oo_dir = os.path.join(tmp_dir,'omniORBpy-'+version)
            build_dir = os.path.join(oo_dir,'build')
            os.mkdir(build_dir)
            mod_env = dict(os.environ)
            if subprocess.call([os.path.join(oo_dir,'configure'),
                                '--prefix', dir_name],
                                cwd=build_dir):
                raise Exception('omniorb.py failed to configure')
            if subprocess.call(['make'],cwd=build_dir):
                raise Exception('omniorbpy failed to make')
            if subprocess.call(['make','install'],cwd=build_dir):
                raise Exception('omniorbpy failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
