# build the /py2-v1 directory, for this OS

import sys
import os
import subprocess
import tempfile
import shutil

from build_util import *

tools = get_tools()

def ports_packages(dir_name):
    """Install I3_PORTS packages"""
    if 'I3_PORTS' not in os.environ:
        raise Exception('$I3_PORTS not defined')
    port_dir = os.environ['I3_PORTS']
    
    tools['i3_ports']['sync']()
    
    packages = ['gsl_1.16','gsl_1.8','gsl_1.14','rdmc_2.9.5','sprng_2.0a',
                'cmake','mysql_4.1.20','boost_1.38.0',
                'anis_1.0','anis_1.8.2','GotoBLAS2 +bulldozer','libxml2_2.7.8',
                'cdk','hdf5_1.8.13','Minuit2_5.24.00',
                'cfitsio_3.37','SuiteSparse','photonics_1.67',
                'photonics_1.73','log4cplus_1.0.2','log4cplus_1.0.4',
                'slalib-c_0.0']#,'healpix']
    
    if os.environ['OS_ARCH'] != 'Ubuntu_14_x86_64':
        packages += ['root_5.34.18 +nox11']#'root_5.28.00d +nox11'
    
    if os.uname()[0].lower() == 'linux':
        packages += ['libarchive','geant4_4.9.5','pythia_root_6.4.16',
                     'root_5.30.06 +mathmore +nox11','genie_2.6.4']
    
    if 'ubuntu' not in os.environ['OS_ARCH'].lower():
        packages += ['qt_4.8.6']#['qt_4.6.4','qt_4.8.6']
    
    for pkg in packages:
        tools['i3_ports']['manual_package'](pkg)

    root_5_24 = os.path.join(port_dir,'root-v5.24.00b')
    if os.path.isdir(root_5_24):
        shutil.rmtree(root_5_24)
    elif os.path.exists(root_5_24) or os.path.islink(root_5_24):
        os.remove(root_5_24)
    os.symlink(os.path.join(port_dir,'root-v5.28.00d'),root_5_24)

def python_packages(dir_name):
    packages = ['numpy==1.7.1','scipy==0.12.0','readline==6.2.4.1',
                'ipython==2.4.0','pyfits==3.1.2','numexpr==2.2.1',
                'Cython==0.19.1','tables==3.0.0',
                'matplotlib==1.4.0','Sphinx==1.1.3','healpy==1.7.3',
                'pyMinuit2==1.1.0','spectrum==0.5.6','urwid==1.1.1',
                'PyMySQL==0.6.1']
    
    if os.environ['OS_ARCH'] == 'RHEL_5_x86_64':
        packages += ['pyOpenSSL==0.12']
    else:
        packages += ['pyOpenSSL==0.13']
    
    packages += ['pyasn1==0.1.7','coverage==3.7.1','flexmock==0.9.7',
                 'pyzmq==14.3.1','tornado==4.0.2']
    
    for pkg in packages:
        tools['pip']['install'](pkg)
    
    # gnuplot-py is special
    tools['pip']['install']('http://downloads.sourceforge.net/project/gnuplot-py/Gnuplot-py/1.8/gnuplot-py-1.8.tar.gz')
    
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
    

def build(src,dest,**build_kwargs):
    """The main builder"""
    # first, make sure the base dir is there
    dir_name = os.path.join(dest,'py2-v1')
    copy_src(os.path.join(src,'py2-v1'),dir_name)
    
    # Cleaning out the PYTHONPATH in case
    # more than one variant gets build
    # otherwise pip will pick up wrong
    # python
    del os.environ["PYTHONPATH"]
    
    # now, do the OS-specific stuff
    load_env(dir_name)
    if 'SROOT' not in os.environ:
        raise Exception('$SROOT not defined')
    dir_name = os.environ['SROOT']
    
    # fill OS-specific directory with dirs
    for d in ('bin','etc','i3ports','include','lib','libexec','man',
              'metaprojects','share','tools'):
        d = os.path.join(dir_name,d)
        if not os.path.exists(d):
            os.makedirs(d)
    # do symlinks
    for src,dest in (('lib','lib64'),('bin','sbin')):
        dest = os.path.join(dir_name,dest)
        if not os.path.exists(dest):
            os.symlink(os.path.join(dir_name,src),dest)
    
    # build software
    tools['tcl_tk']['8.5.14'](dir_name)
    tools['sqlite']['3080600'](dir_name)
    tools['python']['2.7.8'](dir_name)
    tools['python_distribute']['0.6.49'](dir_name)
    tools['pip']['1.4.1'](dir_name)
    
    tools['i3_ports']['base'](dir_name)
    # reload env because ports is stupid
    load_env(os.path.join(dest,'py2-v1'))
    if 'ubuntu' in os.environ['OS_ARCH'].lower():
        tools['qt']['4.8.5'](dir_name)
    #ports_packages(dir_name)
    # reload env because ports is stupid
    load_env(os.path.join(dest,'py2-v1'))
    
    tools['gnuplot']['4.6.3'](dir_name)
    tools['hdf5']['1.8.12'](dir_name)
    tools['zmq']['4.0.4'](dir_name)
    
    # more env for setup
    os.environ['BLAS'] = os.path.join(os.environ['I3_PORTS'],'lib/libgoto2.so')
    os.environ['LAPACK'] = os.path.join(os.environ['I3_PORTS'],'lib/libgoto2.so')
    os.environ['HDF5_DIR'] = os.environ['SROOT']
    os.environ['CFITSIO_EXT_PREFIX'] = os.environ['I3_PORTS']
    
    tools['fftw']['3.3.4'](dir_name)
    tools['healpix']['3.11'](dir_name)
    
    #python_packages(dir_name)
    tools['boostnumpy']['0.2.2'](dir_name,old_boost=True)
    
    tools['globus']['5.2.5'](dir_name)
    tools['gsoap']['2.8.21'](dir_name)
    tools['voms']['2.0.12-2'](dir_name)
    
    
