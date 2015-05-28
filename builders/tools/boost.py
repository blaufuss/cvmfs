"""boost build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'lib','libboost_python.so')):
        print('installing boost version',version)
        name = 'boost_'+version.replace('.','_')+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('http://iweb.dl.sourceforge.net/project/boost/boost',version,name)
            wget(url,path)
            unpack(path,tmp_dir)
            boost_dir = os.path.join(tmp_dir,'boost_'+version.replace('.','_'))
            if subprocess.call([os.path.join(boost_dir,'bootstrap.sh'),
                                '--prefix='+dir_name],cwd=boost_dir):
                raise Exception('boost failed to bootstrap')
            if subprocess.call([os.path.join(boost_dir,'b2'),'install'],cwd=boost_dir):
                raise Exception('boost failed to b2 install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
