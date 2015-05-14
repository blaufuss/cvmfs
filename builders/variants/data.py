# build the /data directory

import os
import subprocess
import tempfile
import shutil

from build_util import *

def gcd(dir_name):
    """Copy GCDs to the data directory"""
    gcd_dir = os.path.join(dir_name,'GCD')
    wget_recursive('http://prod-exe.icecube.wisc.edu/GCD/', gcd_dir+'/')

def test_data(dir_name):
    """Copy the test-data"""
    test_dir = os.path.join(dir_name,'i3-test-data')
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)
    rsync('code.icecube.wisc.edu::Offline/test-data/',test_dir+'/',flags=['-vrlpt','--delete'])

def nugen_tables(dir_name):
    """Copy nugen tables"""
    nugen_dir = os.path.join(dir_name,'neutrino-generator')
    if not os.path.exists(nugen_dir):
        os.mkdir(nugen_dir)
    tmp_dir = tempfile.mkdtemp()
    try:
        tmp_path = os.path.join(tmp_dir,'nugen-v3-tables.tgz')
        md5sum_path = os.path.join(tmp_dir,'nugen-v3-tables.md5sum')
        wget('http://code.icecube.wisc.edu/tools/neutrino-generator/nugen-v3-tables.tgz',tmp_path)
        wget('http://code.icecube.wisc.edu/tools/neutrino-generator/nugen-v3-tables.md5sum',md5sum_path)
        check_md5sum(tmp_path,md5sum=md5sum_path)
        unpack(tmp_path,nugen_dir)
    finally:
        shutil.rmtree(tmp_dir)

def clsim_tables(dir_name):
    """Copy clsim tables"""
    base = 'http://code.icecube.wisc.edu/tools/clsim/'
    tmp_dir = tempfile.mkdtemp()
    try:
        md5sums = os.path.join(tmp_dir,'MD5SUMS')
        wget(os.path.join(base,'MD5SUMS'), md5sums)
        for f in ('safeprimes_base32.gz','safeprimes_base32.txt'):
            path = os.path.join(dir_name,f)
            if not os.path.exists(path):
                wget(os.path.join(base,f), path)
                check_md5sum(path,md5sum=md5sums)
    finally:
        shutil.rmtree(tmp_dir)

def photon_tables(dir_name):
    """Copy photon tables and splines"""
    photon_dir = os.path.join(dir_name,'photon-tables')
    if not os.path.exists(photon_dir):
        os.mkdir(photon_dir)
    spline_dir = os.path.join(photon_dir,'splines')
    if not os.path.exists(spline_dir):
        os.mkdir(spline_dir)
    rsync('data.icecube.wisc.edu:/data/sim/sim-new/PhotonTablesFilteringIC79IC86/',
          photon_dir+'/', flags=['-vrlpt','--delete','--exclude','splines'])
    rsync('data.icecube.wisc.edu:/data/sim/sim-new/spline-tables/',
          spline_dir+'/', flags=['-vrlpt','--delete',])

def voms(dir_name):
    voms_dir = os.path.join(dir_name,'voms')
    if not os.path.exists(voms_dir):
        os.mkdir(voms_dir)
    rsync('data.icecube.wisc.edu:/data/sim/sim-new/voms_data/',
          voms_dir+'/', flags=['-vrlpt','--delete',])

def build(src,dest):
    """The main builder"""
    dir_name = os.path.join(dest,'data')
    
    copy_src(os.path.join(src,'data'),dir_name)
    
    gcd(dir_name)
    #test_data(dir_name)
    nugen_tables(dir_name)
    clsim_tables(dir_name)
    #photon_tables(dir_name)
    voms(dir_name)
