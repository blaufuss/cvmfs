"""cURL build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'bin','curl')):
        print('installing curl version',version)
        name = 'curl-'+str(version)+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('http://curl.haxx.se/download',name)
            wget(url,path)
            unpack(path,tmp_dir)
            curl_dir = os.path.join(tmp_dir,'curl-'+str(version))
            if subprocess.call([os.path.join(curl_dir,'configure'),
                                '--prefix',dir_name],
                                cwd=curl_dir):
                raise Exception('curl failed to configure')
            if subprocess.call(['make'],cwd=curl_dir):
                raise Exception('curl failed to make')
            if subprocess.call(['make','install'],cwd=curl_dir):
                raise Exception('curl failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
