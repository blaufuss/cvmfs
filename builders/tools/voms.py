"""voms build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'bin','voms-proxy-init')):
        print('installing voms version',version)
        name = 'v'+str(version)+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('https://github.com/italiangrid/voms/archive',name)
            wget(url,path)
            unpack(path,tmp_dir)
            voms_dir = os.path.join(tmp_dir,'voms-'+version)
            if subprocess.call([os.path.join(voms_dir,'autogen.sh')],cwd=voms_dir):
                raise Exception('voms failed to autogen')
            if subprocess.call([os.path.join(voms_dir,'configure'),
                                '--prefix',dir_name,'--without-interfaces',
                                '--without-server','--disable-shared',
                                '--with-gsoap-wsdl2h='+os.path.join(dir_name,'bin','wsdl2h')
                               ],cwd=voms_dir):
                raise Exception('voms failed to configure')
            if subprocess.call(['make'],cwd=voms_dir):
                raise Exception('voms failed to make')
            if subprocess.call(['make','install'],cwd=voms_dir):
                raise Exception('voms failed to install')
        finally:
            shutil.rmtree(tmp_dir)

    # make symlinks
    i3_data = os.path.abspath(os.environ['I3_DATA'])
    for path in ('etc/vomsdir','etc/vomses','share/certificates',
                 'share/vomsdir'):
        if not os.path.exists(os.path.join(dir_name,path)):
            os.symlink(os.path.join(data,'voms',path),
                       os.path.join(dir_name,path))

def versions():
    return version_dict(install)
