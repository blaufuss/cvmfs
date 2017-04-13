"""genie build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None,data_dir=None):
    if not os.path.exists(os.path.join(dir_name,'bin','genie')):
        print('installing genie version',version)
        name = 'GENIE-Generator_v'+str(version)+'.tar.gz'
        base_url = 'https://www.hepforge.org/archive/genie/'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join(base_url,name)
            wget(url,path)
            unpack(path,tmp_dir)
            genie_dir = os.path.join(tmp_dir,'GENIE-Generator_v'+version)
            build_dir = os.path.join(tmp_dir,'build')
            os.mkdir(build_dir)
            options = ['--enable-vhe-extension',
                       '--enable-vle-extension',
                       '--enable-rwght',
                       '--with-pythia6-lib='+os.path.join(dir_name,'lib'),
                       '--with-libxml-inc='+os.path.join(dir_name,'include'),
                       '--with-libxml2-lib='+os.path.join(dir_name,'lib'),
                       '--with-log4cpp-inc='+os.path.join(dir_name,'include'),
                       '--with-log4cpp-lib='+os.path.join(dir_name,'lib'),
                      ]
            env = dict(os.environ)
            env['GENIE'] = genie_dir
            if data_dir:
                options.append('-DGEANT4_INSTALL_DATADIR='+data_dir)
            if subprocess.call(['configure',
                                '--prefix='+dir_name,]
                                +options,cwd=build_dir):
                raise Exception('genie failed to cmake')
            if subprocess.call(['gmake'],cwd=build_dir):
                raise Exception('genie failed to make')
            if subprocess.call(['gmake','install'],cwd=build_dir):
                raise Exception('genie failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
