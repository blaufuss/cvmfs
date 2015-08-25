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

def install(dir_name,meta=None,version=None,svn_up=True):
    build_dir = os.path.join(dir_name,'metaprojects',meta,version)
    svn_auth = ['--username','icecube','--password','skua','--non-interactive']
    if not os.path.exists(build_dir) or version == 'trunk':
        print('installing %s %s',(meta,version))
        try:
            if version == 'trunk':
                svn_url = 'http://code.icecube.wisc.edu/svn/meta-projects/%s/trunk'%(meta,)
            else:
                svn_url = 'http://code.icecube.wisc.edu/svn/meta-projects/%s/releases/%s'%(meta,version)
            src_dir = os.path.join(os.environ['SROOTBASE'],'metaprojects',meta,version)
            if svn_up:
                if not os.path.exists(src_dir):
                    if subprocess.call(['svn','co',svn_url,src_dir]+svn_auth):
                        raise Exception('%s %s could not check out source'%(meta,version))
                elif version == 'trunk':
                    if subprocess.call(['svn','up',src_dir]+svn_auth):
                        raise Exception('%s trunk could not update source'%(meta,))
            elif not os.path.exists(src_dir):
                raise Exception('source dir is empty')
            if version == 'trunk':
                if os.path.exists(build_dir):
                    if subprocess.call(['rm','-rf',build_dir],cwd=build_dir):
                        raise Exception('%s trunk could not delete build dir'%(meta,))
            if subprocess.call(['mkdir','-p',build_dir]):
                raise Exception('%s %s cannot create build dir'%(meta,version))
            if subprocess.call(['cmake', '-DCMAKE_BUILD_TYPE=Release',
                                '-DCOPY_PYTHON_DIR=True', src_dir],
                                cwd=build_dir):
                raise Exception('%s %s failed to cmake'%(meta,version))
            if subprocess.call(['make','-j',str(cpu_cores)], cwd=build_dir):
                raise Exception('%s %s failed to cmake'%(meta,version))
        except Exception:
            #if subprocess.call(['rm','-rf',build_dir],cwd=build_dir):
            #    raise Exception('%s %s could not clean up build dir after exception'%(meta,version))
            raise

def versions():
  return {
    'offline-software': version_dict(partial(install,meta='offline-software')),
    'simulation': version_dict(partial(install,meta='simulation')),
    'icerec': version_dict(partial(install,meta='icerec')),
  }
