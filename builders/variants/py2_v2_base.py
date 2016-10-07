# build the /py2-v1 directory, for this OS

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

    packages = []

    if os.uname()[0].lower() == 'linux':
        packages += ['geant4_4.9.5','pythia_root_6.4.16',
                     'root_5.34.18 +mathmore +nox11','genie_2.8.6']

    for pkg in packages:
        tools['i3_ports']['manual_package'](pkg)

def python_packages(dir_name):
    packages = ['setuptools==20.4','numpy==1.9.2','scipy==0.15.1','readline==6.2.4.1',
                'ipython==3.1.0','pyfits==3.3','numexpr==2.4.3',
                'Cython==0.22','PyMySQL==0.6.6','cffi==1.5.0',
                'matplotlib==1.4.3','Sphinx==1.3.1','healpy==1.8.6',
                'spectrum==0.6.0','urwid==1.3.0',
                'urllib3==1.10.4','requests==2.7.0',
                'jsonschema==2.5.1','pyasn1==0.1.8',
               ]

    if os.environ['OS_ARCH'] == 'RHEL_5_x86_64':
        packages += ['pyOpenSSL==0.12']
    else:
        packages += ['pyOpenSSL==0.15.1']

    packages += ['coverage==3.7.1','flexmock==0.9.7',
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


def build(src,dest,**build_kwargs):
    """The main builder"""
    # first, make sure the base dir is there
    dir_name = os.path.join(dest,'py2-v2')
    copy_src(os.path.join(src,'py2-v2'),dir_name)

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

    # RHEL 6 is too old to build newer libtool
    if 'RHEL_6' in os.environ['OS_ARCH']:
        tools['libtool']['2.4.4'](dir_name)
    else:
        tools['libtool']['2.4.6'](dir_name)

    # build core software
    tools['libffi']['3.2.1'](dir_name)
    tools['libarchive']['3.1.2'](dir_name)
    tools['libxml2']['2.9.2'](dir_name)
    tools['sqlite']['3081002'](dir_name)
    tools['tcl_tk']['8.6.4'](dir_name)
    tools['cmake']['3.2.2'](dir_name)
    tools['zmq']['4.0.5'](dir_name)
    tools['python']['2.7.10'](dir_name)
    tools['pip']['latest'](dir_name)

    # build extra software
    tools['qt']['4.8.6'](dir_name)
    #tools['globus']['6.0.1430141288'](dir_name)
    tools['globus']['5.2.5'](dir_name)
    tools['gsoap']['2.8.22'](dir_name)
    tools['voms']['2.0.12-2'](dir_name)

    # build physics software
    tools['gsl']['1.16'](dir_name)
    tools['boost']['1.57.0'](dir_name)
    tools['sprng']['2.0b'](dir_name)
    tools['openblas']['0.2.15'](dir_name)
    tools['suitesparse']['4.4.4'](dir_name)
    tools['cfitsio']['3.370'](dir_name)
    tools['fftw']['3.3.4'](dir_name)
    tools['cdk']['5.0'](dir_name)
    tools['gnuplot']['5.0.0'](dir_name)
    tools['hdf5']['1.8.15'](dir_name)
    tools['erfa']['1.2.0'](dir_name)
    tools['pal']['master'](dir_name)
    tools['healpix']['3.20'](dir_name)

    # build i3ports and difficult software
    tools['i3_ports']['base'](dir_name)
    # reload env because ports is stupid
    load_env(os.path.join(dest,'py2-v2'))
    ports_packages(dir_name)
    # reload env because ports is stupid
    load_env(os.path.join(dest,'py2-v2'))

    # build python software
    python_packages(dir_name)
    tools['boostnumpy']['0.2.2'](dir_name,old_boost=True)

    # copy "tools"
    for t in ('libgfortran',):
        copied = False
        for path in ('/usr/lib','/usr/lib/x86_64-linux-gnu','/lib','/usr/lib64','/lib64'):
            for g in glob.glob(os.path.join(path,t+'*')):
                outname = os.path.join(dir_name,'tools',t.replace('lib',''),os.path.basename(g))
                if not os.path.exists(outname):
                    if not os.path.exists(os.path.dirname(outname)):
                        os.makedirs(os.path.dirname(outname))
                    shutil.copy2(g,outname)
                copied = True
            if copied:
                break
