"""suitesparse build/install"""

import os
import subprocess
import tempfile
import shutil
import copy

from distutils.version import LooseVersion

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if (not (os.path.exists(os.path.join(dir_name,'lib','libsuitesparseconfig.a'))
        or os.path.exists(os.path.join(dir_name,'lib','libsuitesparseconfig.so')))):
        print('installing suitesparse version',version)
        name = 'SuiteSparse-'+version+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('http://faculty.cse.tamu.edu/davis/SuiteSparse',name)
            wget(url,path)
            unpack(path,tmp_dir)
            suitesparse_dir = os.path.join(tmp_dir,'SuiteSparse')
            config_name = os.path.join(suitesparse_dir,'SuiteSparse_config','SuiteSparse_config.mk')
            config = open(config_name).read()
            with open(config_name,'w') as f:
                f.write('BLAS = -L'+os.path.join(dir_name,'lib')+' -lopenblas\n')
                f.write('LAPACK = -L'+os.path.join(dir_name,'lib')+' -lopenblas\n')
                f.write('CFOPENMP=\n')
                for line in config.split('\n'):
                    if line.strip().startswith('INSTALL '):
                        line = 'INSTALL = '+dir_name
                    elif line.strip().startswith('INSTALL_LIB '):
                        line = 'INSTALL_LIB = '+os.path.join(dir_name,'lib')
                    elif line.strip().startswith('INSTALL_INCLUDE '):
                        line = 'INSTALL_INCLUDE = '+os.path.join(dir_name,'include')
                    elif line.strip().startswith('INSTALL_DOC '):
                        docs_dir = os.path.join(dir_name,'share','suitesparse')
                        line = 'INSTALL_DOC = '+docs_dir
                        if not os.path.exists(docs_dir):
                            os.mkdir(docs_dir)
                    elif 'BLAS =' in line or 'LAPACK =' in line or 'CFOPENMP ' in line:
                        line = '#'+line
                    f.write(line+'\n')
            if subprocess.call(['make','library','LDFLAGS=-L'+os.path.join(suitesparse_dir,'lib')],
                                cwd=suitesparse_dir):
                raise Exception('suitesparse failed to make')
            if subprocess.call(['make','install'],cwd=suitesparse_dir):
                raise Exception('suitesparse failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
