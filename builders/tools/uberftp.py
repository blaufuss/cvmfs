"""uberftp build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'bin','uberftp')):
        print('installing uberftp version',version)
        url = 'https://github.com/WIPACrepo/UberFTP/archive/master.tar.gz'
        name = os.path.basename(url)
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            wget(url,path)
            unpack(path,tmp_dir)
            src_dir = os.path.join(tmp_dir,'UberFTP-master')
            if subprocess.call([os.path.join(src_dir,'configure'),
                                '--with-globus='+dir_name,
                                '--with-globus-flavor=gcc64dbg',
                                '--with-globus_config='+os.path.join(dir_name,'include','gcc64dbg'),
                                '--prefix='+dir_name],
                                cwd=src_dir):
                raise Exception('failed to configure')
            if subprocess.call(['make'],cwd=src_dir):
                raise Exception('failed to make')
            if subprocess.call(['make','install'],cwd=src_dir):
                raise Exception('failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
