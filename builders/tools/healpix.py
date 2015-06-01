"""healpix build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None,i3ports=False):
    if not os.path.exists(os.path.join(dir_name,'lib','libchealpix.so')):
        print('installing healpix version',version)
        try:
            tmp_dir = tempfile.mkdtemp()
            name = 'README'
            path = os.path.join(tmp_dir,name)
            url = os.path.join('http://iweb.dl.sourceforge.net/project/healpix/Healpix_'+version,name)
            wget(url,path)
            for line in open(path):
                if 'tar.gz' in line:
                    name = line.strip().strip(':')
                    break
            else:
                raise Exception('healpix: cannot determine tarball name')
            print 'NAME:',name
            url = os.path.join('http://iweb.dl.sourceforge.net/project/healpix/Healpix_'+version,name)
            # the sourceforge retry
            wget(url,path,retry=5)
            unpack(path,tmp_dir)
            healpix_dir = os.path.join(tmp_dir,'Healpix_'+version,'src/C/subs')
            if i3ports:
                i3ports_dir = os.environ['I3_PORTS']
            else:
                i3ports_dir = dir_name
            if subprocess.call(['make','shared',
                                'CFITSIO_INCDIR='+os.path.join(i3ports_dir,'include'),
                                'CFITSIO_LIBDIR='+os.path.join(i3ports_dir,'lib')
                               ],cwd=healpix_dir):
                raise Exception('healpix failed to make')
            if subprocess.call(['make','install',
                                'INCDIR='+os.path.join(dir_name,'include'),
                                'LIBDIR='+os.path.join(dir_name,'lib')
                               ],cwd=healpix_dir):
                raise Exception('healpix failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
