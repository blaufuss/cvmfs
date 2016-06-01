"""sprng build/install"""

import os
import subprocess
import tempfile
import shutil
import string
import glob

from build_util import wget, unpack, version_dict, get_fortran_compiler

def install(dir_name,version=None):
    fortran_compiler=None
    c_compiler=None
    if 'FC' in os.environ:
        fortran_compiler = os.environ['FC']
    if 'CC' in os.environ:
        c_compiler = os.environ['CC']

    if not os.path.exists(os.path.join(dir_name,'lib','libsprng.a')):
        print('installing sprng version',version)
        name = 'sprng'+version+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('http://www.sprng.org/Version'+version.strip(string.ascii_letters),name)
            wget(url,path)
            unpack(path,tmp_dir)
            sprng_dir = os.path.join(tmp_dir,'sprng'+version.strip(string.ascii_letters))
            choices = open(os.path.join(sprng_dir,'make.CHOICES')).read()
            f = open(os.path.join(sprng_dir,'make.CHOICES'),'w')
            try:
                for line in choices.split('\n'):
                    if not line.startswith('#'):
                        line = '#'+line
                    if 'INTEL' in line:
                        line = line[1:]
                    #elif 'LIB_REL_DIR' in line:
                    #    line = 'LIB_REL_DIR  = '+os.path.join(dir_name,'lib')
                    f.write(line+'\n')
            finally:
                f.close()
            make_intel = os.path.join(sprng_dir,'SRC','make.INTEL')
            data = open(make_intel).read()
            if fortran_compiler is not None:
                data = data.replace('g77',fortran_compiler).replace('-DAdd__','-DAdd_')
            else:
                data = data.replace('g77',get_fortran_compiler()).replace('-DAdd__','-DAdd_')
            if c_compiler is not None:
                data = data.replace('gcc',c_compiler).replace('-DAdd__','-DAdd_')
            data = data.replace('CFLAGS = ','CFLAGS = -fPIC ')
            open(make_intel,'w').write(data)
            if subprocess.call(['make','src'],cwd=sprng_dir):
                raise Exception('sprng failed to make')

            # manually install
            install_cmd = ['install','-D']
            if subprocess.call(install_cmd + [os.path.join(sprng_dir,'libsprng.a'),
                               os.path.join(dir_name,'lib','libsprng.a')],cwd=sprng_dir):
                raise Exception('failed to install library')
            install_cmd.extend(['-m','644'])
            include_dir = os.path.join(dir_name,'include','sprng')
            for f in glob.glob(os.path.join(sprng_dir,'include','*.h')):
                if subprocess.call(install_cmd + [f,
                                   os.path.join(include_dir,os.path.basename(f))],
                                   cwd=sprng_dir):
                    raise Exception('failed to install %s'%f)
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
