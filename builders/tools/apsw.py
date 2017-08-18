"""apsw build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unzip, version_dict

def install(dir_name,version=None):
    if subprocess.call(['python','-c','import apsw']):
        print('installing apsw version',version)
        name = 'apsw-'+str(version)+'.zip'
        sqlite_version = version.split('-')[0]
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('https://github.com/rogerbinns/apsw/releases/download',
                               str(version),name)
            wget(url,path)
            unzip(path,tmp_dir)
            apsw_dir = os.path.join(tmp_dir,'apsw-'+str(version))

            if subprocess.call(['python','setup.py','fetch','--all',
                                '--version',sqlite_version,
                                'build','--enable-all-extensions',
                                'install','--prefix',dir_name],
                                cwd=apsw_dir):
                raise Exception('apsw failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
