"""hdf5 build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict, cpu_cores

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'bin','h5ls')):
        print('installing hdf5 version',version)
        name = 'hdf5-'+str(version)+'.tar.gz'
        short_version = '.'.join(version.split('.')[:2])
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join("https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-"+short_version,"hdf5-"+version, 'src', name)
            try:
                wget(url,path)
            except Exception:
                try:
                    url = os.path.join("https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-"+short_version, name)
                    wget(url,path)
                except Exception:
                    url = os.path.join("https://support.hdfgroup.org/ftp/HDF5/current18", 'src', name)
                    wget(url,path)
            unpack(path,tmp_dir,flags=['-xz'])
            hdf5_dir = os.path.join(tmp_dir,'hdf5-'+version)
            if 'CC' in os.environ:
                os.environ['HDF5_CC'] = os.environ['CC']
            if subprocess.call([os.path.join(hdf5_dir,'configure'),
                                '--prefix',dir_name,'--disable-debug',
                                '--enable-cxx','--enable-production',
                                '--enable-strict-format-checks',
                                '--with-zlib=/usr'],cwd=hdf5_dir):
                raise Exception('hdf5 failed to configure')
            if subprocess.call(['make', '-j', cpu_cores],cwd=hdf5_dir):
                raise Exception('hdf5 failed to make')
            if subprocess.call(['make','install'],cwd=hdf5_dir):
                raise Exception('hdf5 failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
