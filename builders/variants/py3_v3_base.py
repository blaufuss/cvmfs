# build the /py3-v3 directory, for this OS

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
    packages = ['setuptools==34.4.1','numpy==1.12.1','scipy==0.19.0','readline==6.2.4.1',
                'ipython==5.3.0','pyfits==3.4','numexpr==2.6.2',
                'Cython==0.25.2','PyMySQL==0.7.11','cffi==1.10.0',
                'matplotlib==2.0.0','Sphinx==1.5.5','healpy==1.10.3',
                'spectrum==0.6.2','urwid==1.3.1',
                'urllib3==1.20','requests==2.13.0',
                'jsonschema==2.6.0','virtualenv==15.1.0',
                'pyOpenSSL==16.2.0','jupyter==1.0.0',
                'pymongo==3.4.0',
               ]

    for pkg in packages:
        tools['pip']['install'](pkg)

    # pyMinuit2 is special
    #tools['pip']['install']('https://github.com/jpivarski/pyminuit2/archive/1.1.1.tar.gz')

    # tables is special
    os.environ['HDF5_DIR'] = os.environ['SROOT']
    tools['pip']['install']('tables==3.4.1')
    del os.environ['HDF5_DIR']

    # pyfftw is special
    if 'CFLAGS' in os.environ:
        old_cflags = os.environ['CFLAGS']
    else:
        old_cflags = None
    os.environ['CFLAGS'] = '-I '+os.path.join(os.environ['SROOT'],'include')
    tools['pip']['install']('pyfftw==0.10.4')
    if old_cflags:
        os.environ['CFLAGS'] = old_cflags
    else:
        del os.environ['CFLAGS']

def build(src,dest,**build_kwargs):
    """The main builder"""
    # make sure the base dir is there
    srootbase = os.path.join(dest,'py3-v3')
    copy_src(os.path.join(src,'py3-v3'),srootbase)

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

    load_env(srootbase, reset=orig_env)

    # build core software
    tools['libtool']['2.4.6'](dir_name)
    tools['m4']['1.4.18'](dir_name)
    tools['pkg-config']['0.29.2'](dir_name)
    tools['libffi']['3.2.1'](dir_name)
    tools['libarchive']['3.3.1'](dir_name)
    tools['libxml2']['2.9.4'](dir_name)
    tools['sqlite']['3180000'](dir_name)
    #tools['tcl_tk']['8.6.6'](dir_name) # only used by i3ports
    tools['python']['3.6.1'](dir_name)
    tools['cmake']['3.7.2'](dir_name)
    tools['log4cpp']['1.1.1'](dir_name)

    tools['zmq']['4.1.6'](dir_name)
    tools['pip']['latest'](dir_name)
    # dropping GUI support
    #tools['qt']['5.8.0'](dir_name)

    # build extra software
    # not happy with ssl 1.1
    #tools['globus']['6.0.1478289945'](dir_name)
    #tools['gsoap']['2.8.45'](dir_name)
    #tools['voms']['2.0.14'](dir_name)

    # build physics software
    tools['gsl']['2.3'](dir_name)
    tools['boost']['1.63.0'](dir_name)
    tools['sprng']['2.0b'](dir_name)
    tools['openblas']['0.2.19'](dir_name)
    tools['suitesparse']['4.5.4'](dir_name)
    tools['cfitsio']['3.410'](dir_name)
    tools['fftw']['3.3.6-pl2'](dir_name)
    tools['cdk']['5.0-20160131'](dir_name)
    tools['gnuplot']['5.0.0'](dir_name)
    tools['hdf5']['1.8.18'](dir_name)
    tools['erfa']['1.3.0'](dir_name)
    tools['pal']['master'](dir_name)
    tools['healpix']['3.31'](dir_name,i3ports=False)
    tools['nlopt']['2.4.2'](dir_name)

    tools['pythia']['6.4.28'](dir_name)
    tools['root']['6.09.02'](dir_name)
    #tools['clhep']['2.3.1.1'](dir_name) # not needed?
    tools['geant4']['10.3.1'](dir_name)
    # waiting for better build script
    #tools['genie']['2.12.04'](dir_name)

    # reload env
    load_env(srootbase, reset=orig_env)

    # build python software
    python_packages(dir_name)
    tools['boostnumpy']['master'](dir_name)
