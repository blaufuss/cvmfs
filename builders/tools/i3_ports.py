"""I3_PORTS build/install"""

import os
import subprocess
import tempfile
import shutil
from functools import partial
import grp

from build_util import *

def install(dir_name):
    """Install base darwinports"""
    if 'I3_PORTS' not in os.environ:
        raise Exception('$I3_PORTS not set')
    i3ports = os.environ['I3_PORTS']
    if not os.path.exists(os.path.join(i3ports,'bin/port')):
        tmp_dir = tempfile.mkdtemp()
        port_source = os.path.join(tmp_dir,'port_source')
        try:
            group = grp.getgrgid(os.getgid())[0]
            svn_cmd = ['svn','co',
                       'http://code.icecube.wisc.edu/icetray-dist/tools/DarwinPorts/trunk',
                       port_source]
            if subprocess.call(svn_cmd):
                raise Exception('cannot svn checkout DarwinPorts')
            port_configure = [os.path.join(port_source,'configure'),
                              '--prefix='+i3ports,
                              '--with-python='+os.path.join(dir_name,'bin','python'),
                              '--with-tcl='+os.path.join(dir_name,'lib'),
                              '--with-tclinclude='+os.path.join(dir_name,'include'),
                              'TCLSH='+os.path.join(dir_name,'bin','tclsh'),
                              '--with-install-group='+group]
            if subprocess.call(port_configure,cwd=port_source):
                raise Exception('cannot configure DarwinPorts')
            if subprocess.call(['make'],cwd=port_source):
                raise Exception('cannot make DarwinPorts')
            if subprocess.call(['make','install'],cwd=port_source):
                raise Exception('cannot make install DarwinPorts')
            # fix config PATH
            config_path = os.path.join(i3ports,'etc/ports/ports.conf')
            data = open(config_path).read()
            with open(config_path,'w') as f:
                for line in data.split('\n'):
                    f.write(line+'\n')
                    if line.startswith('prefix'):
                        f.write('binpath    %s/bin:%s/bin:%s/sbin:/bin:/sbin:/usr/bin:/usr/sbin:/usr/X11R6/bin\n'%(dir_name,i3ports,i3ports))
        finally:
            shutil.rmtree(tmp_dir)

def sync():
    if 'SROOT' not in os.environ:
        raise Exception('$SROOT not set')
    if 'I3_PORTS' not in os.environ:
        raise Exception('$I3_PORTS not set')
    if not os.path.exists(os.path.join(os.environ['I3_PORTS'],'bin/port')):
        raise Exception('$I3_PORTS/bin/port does not exist')
    
    port_source = os.environ['I3_PORTS']
    if subprocess.call(['port','-v','sync'],cwd=port_source):
        raise Exception('cannot sync DarwinPorts')
    if subprocess.call(['port','-v','upgrade','outdated'],cwd=port_source):
        raise Exception('cannot upgrade DarwinPorts')

def package(name):
    """Install package with name"""
    if 'I3_PORTS' not in os.environ:
        raise Exception('$I3_PORTS not set')
    if not os.path.exists(os.path.join(os.environ['I3_PORTS'],'bin','port')):
        raise Exception('$I3_PORTS/bin/port does not exist')
    
    print('installing i3ports package',name)
    port_source = os.environ['I3_PORTS']
    cmd = ['port','-v','install']
    cmd += name.split(' ')
    if subprocess.call(cmd,cwd=port_source):
        raise Exception('cannot install port: '+name)

def versions():
    return {
        'base':install,
        'sync':sync,
        'i3-tools-v5':partial(package,'i3-tools-v5'),
        'manual_package':package,
    }
