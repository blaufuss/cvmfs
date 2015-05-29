"""sprng build/install"""

import os
import subprocess
import tempfile
import shutil
import string
import glob

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
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
            open(make_intel,'w').write(data.replace('g77','f77').replace('-DAdd__','-DAdd_'))
            makefile = os.path.join(sprng_dir,'Makefile')
            data = open(makefile).read()
            open(makefile,'w').write(data.replace('all : src examples tests','all : src'))
            if subprocess.call(['make'],cwd=sprng_dir):
                raise Exception('sprng failed to make')
            
            # manually install
            shutil.copy2(os.path.join(sprng_dir,'libsprng.a'),
                         os.path.join(dir_name,'lib','libsprng.a'))
            include_dir = os.path.join(dir_name,'include','spring')
            if not os.path.isdir(include_dir):
                os.mkdir(include_dir)
            for f in glob.glob(os.path.join(sprng_dir,'include','*.h')):
                shutil.copy2(f,os.path.join(include_dir,os.path.basename(f)))
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
