"""cdk build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'lib','libcdk.a')):
        print('installing cdk version',version)
        name = 'cdk-'+version+'.tgz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('ftp://ftp.invisible-island.net/cdk',name)
            wget(url,path)
            unpack(path,tmp_dir)
            cdk_dir = os.path.join(tmp_dir,'cdk-'+version)
            if subprocess.call([os.path.join(cdk_dir,'configure'),
                                '--prefix',dir_name],cwd=cdk_dir):
                raise Exception('cdk failed to configure')
            if subprocess.call(['make'],cwd=cdk_dir):
                raise Exception('cdk failed to make')
            if subprocess.call(['make','install'],cwd=cdk_dir):
                raise Exception('cdk failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
