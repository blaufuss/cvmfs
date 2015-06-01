"""erfa build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'lib','liberfa.so')):
        print('installing erfa version',version)
        name = 'erfa-'+str(version)+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('https://github.com/liberfa/erfa/releases/download/v'+version,name)
            wget(url,path)
            unpack(path,tmp_dir)
            erfa_dir = os.path.join(tmp_dir,'erfa-'+version)
            if subprocess.call([os.path.join(erfa_dir,'configure'),
                                '--prefix',dir_name],
                               cwd=erfa_dir):
                raise Exception('erfa failed to configure')
            if subprocess.call(['make'],cwd=erfa_dir):
                raise Exception('erfa failed to make')
            if subprocess.call(['make','install'],cwd=erfa_dir):
                raise Exception('erfa failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
