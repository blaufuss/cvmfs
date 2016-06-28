"""libtool build/install"""

import os
import subprocess
import tempfile
import shutil
from functools import partial

from build_util import wget, unpack, version_dict

try:
    import multiprocessing
    cpu_cores = multiprocessing.cpu_count()
except ImportError:
    cpu_cores = 1

def is_release(version):
    return version not in ('trunk','stable')

def install(dir_name,meta=None,version=None,svn_up=True):
    build_dir = os.path.join(dir_name,'metaprojects',meta,version)
    svn_auth = ['--username','icecube','--password','skua','--non-interactive']
    if not os.path.exists(build_dir) or not is_release(version):
        print('installing %s %s',(meta,version))
        try:
            if is_release(version):
                svn_url = 'http://code.icecube.wisc.edu/svn/meta-projects/%s/releases/%s'%(meta,version)
            else:
                svn_url = 'http://code.icecube.wisc.edu/svn/meta-projects/%s/%s'%(meta,version)
            src_dir = os.path.join(os.environ['SROOTBASE'],'metaprojects',meta,version)
            if svn_up:
                if not is_release(version):
                    shutil.rmtree(src_dir)
                if not os.path.exists(src_dir):
                    if subprocess.call(['svn','co',svn_url,src_dir]+svn_auth):
                        raise Exception('%s %s could not check out source'%(meta,version))
            elif not os.path.exists(src_dir):
                raise Exception('source dir is empty')
            if (not is_release(version)) and os.path.exists(build_dir):
                shutil.rmtree(build_dir)
            os.makedirs(build_dir):
            if subprocess.call(['cmake', '-DCMAKE_BUILD_TYPE=Release',
                                '-DCOPY_PYTHON_DIR=True', src_dir],
                                cwd=build_dir):
                raise Exception('%s %s failed to cmake'%(meta,version))
            if subprocess.call(['make','-j',str(cpu_cores)], cwd=build_dir):
                raise Exception('%s %s failed to cmake'%(meta,version))
        except Exception:
            shutil.rmtree(build_dir)
            raise

def versions():
  return {
    'offline-software': version_dict(partial(install,meta='offline-software')),
    'simulation': version_dict(partial(install,meta='simulation')),
    'icerec': version_dict(partial(install,meta='icerec')),
    'combo': version_dict(partial(install,meta='combo')),
  }
