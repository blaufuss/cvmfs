"""log4cpp build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'lib','liblog4cpp.so')):
        print('installing log4cpp version',version)
        if version > '1.2.0':
            raise Exception('unsupported version')
        name = 'log4cpp-'+str(version)+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('http://downloads.sourceforge.net/project/log4cpp/log4cpp-1.1.x (new)/log4cpp-1.1',name)
            wget(url,path)
            unpack(path,tmp_dir)
            log4cpp_dir = os.path.join(tmp_dir,'log4cpp')
            if subprocess.call([os.path.join(log4cpp_dir,'configure'),
                                '--prefix',dir_name],cwd=log4cpp_dir):
                raise Exception('log4cpp failed to configure')
            if subprocess.call(['make'],cwd=log4cpp_dir):
                raise Exception('log4cpp failed to make')
            if subprocess.call(['make','install'],cwd=log4cpp_dir):
                raise Exception('log4cpp failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
