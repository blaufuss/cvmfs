"""Python build/install"""

import os
import subprocess
import tempfile
import shutil

from distutils.version import LooseVersion
from build_util import wget, unpack, version_dict, cpu_cores

def symlink(target,dest):
    if not os.path.exists(dest):
        curdir = os.getcwd()
        try:
            os.chdir(os.path.dirname(target))
            os.symlink(os.path.basename(target),os.path.basename(dest))
        finally:
            os.chdir(curdir)

def install(dir_name,version=None,pgo=False):
    if not os.path.exists(os.path.join(dir_name,'bin','python')):
        print('installing python version',version)
        name = 'Python-'+str(version)+'.tgz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('http://www.python.org/ftp/python',version,name)
            wget(url,path)
            unpack(path,tmp_dir)
            python_dir = os.path.join(tmp_dir,'Python-'+version)
            options = ['--enable-shared']
            v = LooseVersion(version)
            if v.version[0] < 3 or (v.version[0] == 3 and v.version[1] < 3):
                # 3.3+ is ucs4 by default, set it for older pythons
                options.append('--enable-unicode=ucs4')
            if pgo and (v.version[0] > 3 or (v.version[0] == 3 and v.version[1] > 5)):
                options.append('--enable-optimizations')
                os_arch = os.environ['OS_ARCH'].split('_')
                if ((os_arch[0] == 'RHEL' and float(os_arch[1]) > 7)
                    or (os_arch[0] == 'Ubuntu' and os_arch[1] not in ('12.04','14.04'))):
                    options.append('--with-lto')
            if subprocess.call([os.path.join(python_dir,'configure'),
                                '--prefix',dir_name,]+options
                               ,cwd=python_dir):
                raise Exception('python failed to configure')
            if subprocess.call(['make','-j',cpu_cores],cwd=python_dir):
                raise Exception('python failed to make')
            if subprocess.call(['make','install'],cwd=python_dir):
                raise Exception('python failed to install')
            # Python 3 specific symlinks
            # Assumes no python2 version is installed
            if v.version[0] == 3:
                version_short = '.'.join(map(str, v.version[:2]))
                symlink(os.path.join(dir_name,'bin','python3'),
                        os.path.join(dir_name,'bin','python'))
                symlink(os.path.join(dir_name, 'bin', 'python3-config'),
                        os.path.join(dir_name, 'bin', 'python-config'))
                symlink(os.path.join(dir_name, 'lib', 'pkgconfig', 'python3.pc'),
                        os.path.join(dir_name, 'lib', 'pkgconfig', 'python.pc'))
                symlink(os.path.join(dir_name, 'include', 'python%sm' % version_short),
                        os.path.join(dir_name, 'include', 'python%s' % version_short))
                symlink(os.path.join(dir_name,'bin','pip3'),
                        os.path.join(dir_name,'bin','pip'))
            # check for modules
            for m in ('sqlite3','zlib','bz2','_ssl','_curses','readline'):
                if subprocess.call([os.path.join(dir_name,'bin','python'),
                                    '-c','import '+m]):
                    if os.path.exists(os.path.join(dir_name,'bin','python')):
                        os.remove(os.path.join(dir_name,'bin','python'))
                    raise Exception('failed to build with '+m+' support')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
