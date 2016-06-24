"""gnuplot build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'bin','gnuplot')):
        print('installing gnuplot version',version)
        name = 'gnuplot-'+str(version)+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('http://downloads.sourceforge.net/project/gnuplot/gnuplot/',version,name)
            wget(url,path)
            unpack(path,tmp_dir)
            gnuplot_dir = os.path.join(tmp_dir,'gnuplot-'+version)
            if subprocess.call([os.path.join(gnuplot_dir,'configure'),
                                '--prefix',dir_name,'--without-linux-vga',
                                '--without-lisp-files','--without-tutorial',
                                '--with-bitmap-terminals'],cwd=gnuplot_dir):
                raise Exception('gnuplot failed to configure')
            if subprocess.call(['make'],cwd=gnuplot_dir):
                raise Exception('gnuplot failed to make')
            # touch two files to convince make they are new again
            for f in (os.path.join(gnuplot_dir,'docs','gnuplot-eldoc.el'),
                      os.path.join(gnuplot_dir,'docs','gnuplot-eldoc.elc')):
                if os.path.exists(f):
                    os.utime(f,None)
            if subprocess.call(['make','install'],cwd=gnuplot_dir):
                raise Exception('gnuplot failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
