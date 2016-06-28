"""Python build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'bin','qmake')):
        print('installing qt version',version)
        name = 'qt-everywhere-opensource-src-'+version+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            major_version = '.'.join(version.split('.')[:2])
            url = os.path.join('http://download.qt-project.org/archive/qt/',major_version,version,name)
            wget(url,path)
            unpack(path,tmp_dir)
            qt_dir = os.path.join(tmp_dir,'qt-everywhere-opensource-src-'+version)
            
            # confirm the license early so it doesn't pause for user input
            cfg_path = os.path.join(qt_dir,'configure')
            cfg_data = open(cfg_path).read().replace('OPT_CONFIRM_LICENSE=no','OPT_CONFIRM_LICENSE=yes')
            open(cfg_path,'w').write(cfg_data)
            
            # only install the required components
            if subprocess.call([cfg_path,'-prefix',dir_name,
                                '-opensource','-opengl','-no-accessibility','-no-sql-db2',
                                '-no-sql-ibase','-no-sql-mysql','-no-sql-oci','-no-sql-odbc',
                                '-no-sql-psql','-no-sql-sqlite','-no-sql-sqlite2',
                                '-no-sql-sqlite_symbian','-no-sql-tds',
                                '-no-xmlpatterns','-no-multimedia','-no-phonon','-no-phonon-backend',
                                '-no-webkit','-no-javascript-jit','-no-script','-no-scripttools',
                                '-no-declarative','-no-nis','-nomake','examples','-nomake','demos',
                                '-nomake','docs','-nomake','translations','-fast','-silent']
                               ,cwd=qt_dir):
                raise Exception('qt failed to configure')
            if subprocess.call(['make'],cwd=qt_dir):
                raise Exception('qt failed to make')
            if subprocess.call(['make','install'],cwd=qt_dir):
                raise Exception('qt failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
