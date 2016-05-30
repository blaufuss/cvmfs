# build the /py2-v3 directory, for this OS

import sys
import os
import subprocess
import tempfile
import shutil
import glob

from build_util import *

tools = get_tools()

def ports_packages(dir_name):
    """Install I3_PORTS packages"""
    if 'I3_PORTS' not in os.environ:
        raise Exception('$I3_PORTS not defined')
    port_dir = os.environ['I3_PORTS']

    tools['i3_ports']['sync']()

    packages = []#['Minuit2_5.24.00']

    #if os.environ['OS_ARCH'] != 'Ubuntu_14_x86_64':
    #    packages += ['root_5.34.18 +nox11']

    if os.uname()[0].lower() == 'linux':
        packages += ['geant4_4.9.5','pythia_root_6.4.16',
                     'root_5.34.18 +mathmore +nox11','genie_2.8.6']

    for pkg in packages:
        tools['i3_ports']['manual_package'](pkg)

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

    # fails to install:
    # # gnuplot-py is special
    # tools['pip']['install']('http://iweb.dl.sourceforge.net/project/gnuplot-py/Gnuplot-py/1.8/gnuplot-py-1.8.tar.gz')

    # fails to install:
    # # pyMinuit2 is special
    # tools['pip']['install']('https://github.com/jpivarski/pyminuit2/archive/1.1.0.tar.gz')

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

def create_os_specific_dirs(dir_name):
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


def build(src,dest,**build_kwargs):
    """The main builder"""
    # first, make sure the base dir is there
    dir_name = os.path.join(dest,'py2-v3')
    copy_src(os.path.join(src,'py2-v3'),dir_name)

    # now, do the OS-specific stuff
    load_env(dir_name)
    if 'SROOT' not in os.environ:
        raise Exception('$SROOT not defined')
    dir_name = os.environ['SROOT']

    # fill OS-specific directory with dirs
    create_os_specific_dirs(dir_name)

    # install a temporary gcc in order to bootstrap clang
    if not os.path.exists(os.path.join(dir_name,'bin','clang')):
        # use the system compiler for this, we don't have clang yet
        orig_environ = os.environ
        del os.environ['CC']
        del os.environ['CXX']

        # create a temporary area to install all
        # tools necessart to needed compile
        # a gcc which we will then use to bootstrap
        # clang
        clang_bootstrap_dir_name = os.path.join(dir_name,'clang_bootstrap')
        if not os.path.exists(clang_bootstrap_dir_name):
            os.makedirs(clang_bootstrap_dir_name)
        create_os_specific_dirs(clang_bootstrap_dir_name)

        if 'PATH' in os.environ:
            os.environ['PATH']=os.path.join(clang_bootstrap_dir_name,'bin')+':'+os.environ['PATH']
        else:
            os.environ['PATH']=os.path.join(clang_bootstrap_dir_name,'bin')

        # gcc build dependencies
        tools['gmp']['6.0.0a'](clang_bootstrap_dir_name)
        tools['mpfr']['3.1.3'](clang_bootstrap_dir_name)
        tools['mpc']['1.0.3'](clang_bootstrap_dir_name)
        tools['isl']['0.14'](clang_bootstrap_dir_name)
        tools['m4']['1.4.17'](clang_bootstrap_dir_name)
        tools['bison']['3.0.4'](clang_bootstrap_dir_name)
        tools['flex']['2.6.0'](clang_bootstrap_dir_name)

        # install a temporary gcc (5.2.0 has been tested
        # for bootstrapping, you might want to switch
        # to a more recent version)
        tools['gcc']['5.2.0'](clang_bootstrap_dir_name)

        # now point to the new compiler
        os.environ['CC'] = os.path.join(clang_bootstrap_dir_name,'bin/gcc')
        os.environ['CXX'] = os.path.join(clang_bootstrap_dir_name,'bin/g++')
        os.environ['LD_LIBRARY_PATH']=os.path.join(clang_bootstrap_dir_name,'lib')+':'+os.path.join(clang_bootstrap_dir_name,'lib64')

        # build some more clang build requirements (basically just a modern python and cmake)
        tools['xz']['5.2.2'](clang_bootstrap_dir_name)
        tools['readline']['6.3'](clang_bootstrap_dir_name)
        tools['sqlite']['3081002'](clang_bootstrap_dir_name)
        tools['python']['2.7.10'](clang_bootstrap_dir_name)
        os.environ['PYTHONPATH']=os.path.join(clang_bootstrap_dir_name,'lib/python2.7/site-packages')
        tools['cmake']['3.5.2'](clang_bootstrap_dir_name)

        # build a temporary clang which we will then use to build the final version
        tools['clang']['3.8.0'](clang_bootstrap_dir_name)

        # now, finally build the actual clang we want using
        # the temporary clang we just built
        os.environ['CC'] = os.path.join(clang_bootstrap_dir_name,'bin/clang')
        os.environ['CXX'] = os.path.join(clang_bootstrap_dir_name,'bin/clang++')
        tools['clang']['3.8.0'](dir_name)

        # restore the environment
        os.environ = orig_environ

    # build core software
    tools['m4']['1.4.17'](dir_name)
    tools['libtool']['2.4.6'](dir_name)
    tools['pkg-config']['0.29.1'](dir_name)
    tools['libffi']['3.2.1'](dir_name)
    tools['libarchive']['3.1.2'](dir_name)
    tools['libxml2']['2.9.2'](dir_name)
    tools['readline']['6.3'](dir_name)
    tools['sqlite']['3081002'](dir_name)
    tools['tcl_tk']['8.6.4'](dir_name)
    tools['cmake']['3.5.2'](dir_name)
    tools['zmq']['4.1.4'](dir_name)
    tools['python']['2.7.10'](dir_name)
    tools['pip']['latest'](dir_name)

    ############ GFORTRAN

    # we might not want to do this.. not sure about the benefits
    # - and it pollutes the environment with lots of stuff..

    # install gfortran
    tools['gmp']['6.0.0a'](dir_name)
    tools['mpfr']['3.1.3'](dir_name)
    tools['mpc']['1.0.3'](dir_name)
    tools['isl']['0.14'](dir_name)
    tools['bison']['3.0.4'](dir_name)
    tools['flex']['2.6.0'](dir_name)

    tools['gfortran']['6.1.0'](dir_name)
    # clean up after gcc/gofortran (we specified it should only install fortran and c, but that setting seems to be a lie)
    if (os.path.lexists(os.path.join(dir_name,'bin/cpp'))):
        os.remove(os.path.join(dir_name,'bin/cpp'))
    if (os.path.lexists(os.path.join(dir_name,'bin/gcc'))):
        os.remove(os.path.join(dir_name,'bin/gcc'))
    if (os.path.lexists(os.path.join(dir_name,'bin/g++'))):
        os.remove(os.path.join(dir_name,'bin/g++'))
    if (os.path.lexists(os.path.join(dir_name,'bin/c++'))):
        os.remove(os.path.join(dir_name,'bin/c++'))
    if (os.path.lexists(os.path.join(dir_name,'bin/cc'))):
        os.remove(os.path.join(dir_name,'bin/cc'))
    if not os.path.exists(os.path.join(dir_name,'cc')):
        os.symlink(os.path.join(dir_name,'bin/clang'),os.path.join(dir_name,'bin/cc'))
    if not os.path.exists(os.path.join(dir_name,'c++')):
        os.symlink(os.path.join(dir_name,'bin/clang++'),os.path.join(dir_name,'bin/c++'))
    os.environ['FC'] = os.path.join(dir_name,'bin/gfortran')
    ############ END GFORTRAN

    # build extra software
    # TODO: none of these compile yet (on the cobalts)
    #tools['qt']['4.8.6'](dir_name) # does not compile
    #tools['globus']['6.0.1430141288'](dir_name) # does not compile
    #tools['globus']['5.2.5'](dir_name) # does not compile
    #tools['gsoap']['2.8.22'](dir_name) # does not compile
    #tools['voms']['2.0.12-2'](dir_name) # does not compile

    # build physics software
    tools['gsl']['1.16'](dir_name)
    tools['boost']['1.57.0'](dir_name,for_clang=True)
    tools['sprng']['2.0b'](dir_name)
    tools['openblas']['0.2.15'](dir_name)
    tools['suitesparse']['4.4.4'](dir_name)
    tools['cfitsio']['3.370'](dir_name)
    tools['fftw']['3.3.4'](dir_name)
    tools['cdk']['5.0'](dir_name)
    # tools['gnuplot']['5.0.0'](dir_name) # did not compile
    tools['hdf5']['1.8.15'](dir_name)
    tools['erfa']['1.2.0'](dir_name)
    tools['pal']['master'](dir_name)
    tools['healpix']['3.20'](dir_name,for_clang=True,i3ports=False)

    # build i3ports and difficult software
    tools['i3_ports']['base'](dir_name)
    # reload env because ports is stupid
    load_env(os.path.join(dest,'py2-v3'))
    #ports_packages(dir_name)  # don't even bother yet...
    # reload env because ports is stupid
    load_env(os.path.join(dest,'py2-v3'))

    # build python software
    python_packages(dir_name)
    # tools['boostnumpy']['0.2.2'](dir_name,old_boost=True) # fails to compile with a c++11 error
