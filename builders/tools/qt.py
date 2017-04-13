"""Python build/install"""

import os
import subprocess
import tempfile
import shutil

try:
    import multiprocessing
    cpu_cores = multiprocessing.cpu_count()
except ImportError:
    cpu_cores = 1

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'bin','qmake')):
        print('installing qt version',version)
        name = 'qt-everywhere-opensource-src-'+version+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            major_version = '.'.join(version.split('.')[:2])
            if major_version == '4.8':
                url = os.path.join('http://download.qt.io/archive/qt/',major_version,version,name)
            else:
                url = os.path.join('http://download.qt.io/archive/qt/',major_version,version,'single',name)
            wget(url,path)
            unpack(path,tmp_dir)
            qt_dir = os.path.join(tmp_dir,'qt-everywhere-opensource-src-'+version)

            options = [
                   '-opensource','-opengl','-no-accessibility','-no-sql-db2',
                   '-no-sql-ibase','-no-sql-mysql','-no-sql-oci','-no-sql-odbc',
                   '-no-sql-psql','-no-sql-sqlite','-no-sql-sqlite2', '-no-sql-tds',
                   '-nomake','examples',
            ]

            cfg_path = os.path.join(qt_dir,'configure')
            if major_version == '4.8':
                # confirm the license early so it doesn't pause for user input
                cfg_data = open(cfg_path).read().replace('OPT_CONFIRM_LICENSE=no','OPT_CONFIRM_LICENSE=yes')
                open(cfg_path,'w').write(cfg_data)
                options.extend([
                        '-no-sql-sqlite_symbian',
                        '-no-xmlpatterns','-no-multimedia','-no-phonon','-no-phonon-backend',
                        '-no-webkit','-no-javascript-jit','-no-script','-no-scripttools',
                        '-no-declarative','-no-nis','-fast','-nomake','demos',
                        '-nomake','docs','-nomake','translations',
                ])
            else:
                cpu_cores = 1 # bug in dependencies
                options.extend([
                        '-confirm-license','-no-avx','-no-avx2','-no-avx512',
                        '-no-dbus','--no-harfbuzz','-no-ssl','-skip','wayland',
                ])

            # only install the required components
            if subprocess.call([cfg_path,'-prefix',dir_name]+options
                               ,cwd=qt_dir):
                raise Exception('qt failed to configure')
            if subprocess.call(['make','-j',str(cpu_cores)],cwd=qt_dir):
                raise Exception('qt failed to make')
            if subprocess.call(['make','install'],cwd=qt_dir):
                raise Exception('qt failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
