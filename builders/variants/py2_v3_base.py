# build the /py2-v3 directory, for this OS

import sys
import os
import subprocess
import tempfile
import shutil
import glob
from contextlib import contextmanager

from build_util import *

tools = get_tools()

def python_packages(dir_name):
    packages = ['setuptools==20.4','numpy==1.9.2','scipy==0.15.1','readline==6.2.4.1',
                'ipython==3.1.0','pyfits==3.3','numexpr==2.4.3',
                'Cython==0.22','PyMySQL==0.6.6','cffi==1.1.0',
                'matplotlib==1.4.3','Sphinx==1.3.1','healpy==1.8.6',
                'spectrum==0.6.0','urwid==1.3.0',
                'urllib3==1.10.4','requests==2.7.0',
                'jsonschema==2.5.1','virtualenv==15.0.2',
                'requests==2.10.0'
               ]

    if os.environ['OS_ARCH'] == 'RHEL_5_x86_64':
        packages += ['pyOpenSSL==0.12']
    else:
        packages += ['pyOpenSSL==0.15.1']

    packages += ['pyasn1==0.1.7','coverage==3.7.1','flexmock==0.9.7',
                 'pyzmq==14.6.0','tornado==4.2']

    for pkg in packages:
        tools['pip']['install'](pkg)

    # gnuplot-py is special
    tools['pip']['install']('http://downloads.sourceforge.net/project/gnuplot-py/Gnuplot-py/1.8/gnuplot-py-1.8.tar.gz')

    # pyMinuit2 is special
    tools['pip']['install']('https://github.com/jpivarski/pyminuit2/archive/1.1.0.tar.gz')

    # tables is special
    os.environ['HDF5_DIR'] = os.environ['SROOT']
    tools['pip']['install']('tables==3.2.0')
    del os.environ['HDF5_DIR']

    # tables is special
    os.environ['HDF5_DIR'] = os.environ['SROOT']
    tools['pip']['install']('tables==3.2.0')
    del os.environ['HDF5_DIR']

    # pyfftw is special
    if 'CFLAGS' in os.environ:
        old_cflags = os.environ['CFLAGS']
    else:
        old_cflags = None
    os.environ['CFLAGS'] = '-I '+os.path.join(os.environ['SROOT'],'include')
    tools['pip']['install']('pyfftw==0.9.2')
    if old_cflags:
        os.environ['CFLAGS'] = old_cflags
    else:
        del os.environ['CFLAGS']

@contextmanager
def clang_env(orig_env, srootbase):
    """Build a separate clang env on scratch"""
    dir_name = tempfile.mkdtemp()
    try:
        # fill OS-specific directory with dirs
        for d in ('bin','etc','include','lib','libexec','man',
                  'metaprojects','share','tools'):
            d = os.path.join(dir_name,d)
            if not os.path.exists(d):
                os.makedirs(d)
        # do symlinks
        for src,dest in (('lib','lib64'),('bin','sbin')):
            dest = os.path.join(dir_name,dest)
            if not os.path.exists(dest):
                os.symlink(os.path.join(dir_name,src),dest)

        # set environment
        os.environ['PATH'] = os.path.join(dir_name,'bin')+':'+os.environ['PATH']
        os.environ['LD_LIBRARY_PATH'] = os.path.join(dir_name,'lib')+':'+os.environ['LD_LIBRARY_PATH']
        os.environ['PYTHONPATH'] = os.path.join(dir_name,'lib','python2.7','site-packages')

        # build clang dependencies
        tools['libtool']['2.4.6'](dir_name)
        tools['m4']['1.4.17'](dir_name)
        tools['pkg-config']['0.29.1'](dir_name)
        tools['libxml2']['2.9.4'](dir_name)
        tools['sqlite']['3140100'](dir_name)
        tools['python']['2.7.12'](dir_name)
        tools['cmake']['3.6.1'](dir_name)

        # build clang
        tools['clang']['3.8.0'](dir_name, extras=False)

        # use the env
        load_env(srootbase)
        #for k in ('CC','CXX'):
        #    if k in orig_env:
        #        os.environ[k] = orig_env[k]
        #    else:
        #        del os.environ[k]
        os.environ['CC'] = os.path.join(dir_name,'bin','clang')
        os.environ['CXX'] = os.path.join(dir_name,'bin','clang++')
        yield

    finally:
        pass #shutil.rmtree(dir_name)

def build(src,dest,**build_kwargs):
    """The main builder"""
    # make sure the base dir is there
    srootbase = os.path.join(dest,'py2-v3')
    copy_src(os.path.join(src,'py2-v3'),srootbase)

    orig_env = os.environ.copy()

    # get the SROOT
    dir_name = get_sroot(srootbase)

    # fill OS-specific directory with dirs
    for d in ('bin','etc','include','lib','libexec','man',
              'metaprojects','share','tools'):
        d = os.path.join(dir_name,d)
        if not os.path.exists(d):
            os.makedirs(d)
    # do symlinks
    for src,dest in (('lib','lib64'),('bin','sbin')):
        dest = os.path.join(dir_name,dest)
        if not os.path.exists(dest):
            os.symlink(os.path.join(dir_name,src),dest)

    # build the clang bootstrapping env
    if not os.path.exists(os.path.join(dir_name,'bin','clang')):
        with clang_env(orig_env,srootbase):
            # install clang
            tools['clang']['3.8.1'](dir_name)

    raise Exception()
    # reload env
    load_env(srootbase, reset=orig_env)

    # build core software
    tools['libtool']['2.4.6'](dir_name)
    tools['m4']['1.4.17'](dir_name)
    tools['pkg-config']['0.29.1'](dir_name)
    tools['libffi']['3.2.1'](dir_name)
    tools['libarchive']['3.1.2'](dir_name)
    tools['libxml2']['2.9.4'](dir_name)
    tools['sqlite']['3140100'](dir_name)
    tools['tcl_tk']['8.6.6'](dir_name)
    tools['python']['2.7.12'](dir_name)
    tools['cmake']['3.6.1'](dir_name)
    tools['log4cpp']['1.1.1'](dir_name)

    tools['zmq']['4.1.5'](dir_name)
    tools['pip']['latest'](dir_name)
    tools['qt']['4.8.6'](dir_name)

    # build extra software
    tools['globus']['6.0.1470089956'](dir_name)
    tools['gsoap']['2.8.33'](dir_name)
    tools['voms']['2.0.13'](dir_name)

    # build physics software
    tools['gsl']['2.1'](dir_name)
    tools['boost']['1.61.0'](dir_name,for_clang=True)
    tools['sprng']['2.0b'](dir_name)
    tools['openblas']['0.2.18'](dir_name)
    tools['suitesparse']['4.4.6'](dir_name)
    tools['cfitsio']['3.390'](dir_name)
    tools['fftw']['3.3.5'](dir_name)
    tools['cdk']['5.0-20160131'](dir_name)
    tools['gnuplot']['5.0.0'](dir_name)
    tools['hdf5']['1.8.17'](dir_name)
    tools['erfa']['1.2.0'](dir_name)
    tools['pal']['master'](dir_name)
    tools['healpix']['3.30'](dir_name,for_clang=True,i3ports=False)

    tools['pythia']['6.4.28'](dir_name)
    tools['root']['6.06.06'](dir_name)
    #tools['clhep']['2.3.1.1'](dir_name) # not needed?
    tools['geant4']['10.2.2'](dir_name)
    tools['genie']['2.10.10'](dir_name)

    # reload env
    load_env(srootbase, reset=orig_env)

    # build python software
    python_packages(dir_name)
    tools['boostnumpy']['master'](dir_name,for_clang=True)
