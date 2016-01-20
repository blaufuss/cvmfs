"""pal build/install"""

import os
import subprocess
import tempfile
import shutil
import copy

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'lib','libpal.so')):
        print('installing pal version',version)
        name = version+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('https://github.com/IceCube-SPNO/pal/archive/'+version,name)
            wget(url,path)
            unpack(path,tmp_dir)
            pal_dir = os.path.join(tmp_dir,'pal-'+version)
            m4_dir = os.path.join(pal_dir,'m4')
            if not os.path.exists(m4_dir):
                os.mkdir(m4_dir)

            cfg_path = os.path.join(pal_dir,'configure.ac')
            cfg_data = open(cfg_path).read().replace('2.69','2.63')
            open(cfg_path,'w').write(cfg_data)

            mod_env = copy.deepcopy(os.environ)
            mod_env['LDFLAGS'] = '-L'+os.path.join(dir_name,'lib')
            if 'LDFLAGS' in os.environ:
                mod_env['LDFLAGS'] += ' '+os.environ['LDFLAGS']
            if subprocess.call(['autoreconf','--install','--symlink','.'],
                               env=mod_env,cwd=pal_dir):
                raise Exception('pal failed to bootstrap')
            if subprocess.call([os.path.join(pal_dir,'configure'),
                                '--prefix',dir_name],
                               cwd=pal_dir):
                raise Exception('pal failed to configure')
            if subprocess.call(['make'],cwd=pal_dir):
                raise Exception('pal failed to make')
            if subprocess.call(['make','install'],cwd=pal_dir):
                raise Exception('pal failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
