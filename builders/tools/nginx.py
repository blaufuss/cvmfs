"""Nginx build/install"""

import os
import subprocess
import tempfile
import shutil

from build_util import wget, unpack, version_dict

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'bin','nginx')):
        print('installing nginx version',version)
        name = 'nginx-'+str(version)+'.tar.gz'
        try:
            tmp_dir = tempfile.mkdtemp()
            path = os.path.join(tmp_dir,name)
            url = os.path.join('http://nginx.org/download',name)
            wget(url,path)
            unpack(path,tmp_dir)
            nginx_dir = os.path.join(tmp_dir,'nginx-'+str(version))
            options = ['--with-ipv6','--with-http_ssl_module',
                       '--without-http_geo_module',
                       '--without-http_map_module',
                       '--without-http_fastcgi_module',
                       '--without-http_uwsgi_module',
                       '--without-http_scgi_module',
                       '--without-http_memcached_module',
                       '--without-http_rewrite_module',
                       '--without-mail_pop3_module',
                       '--without-mail_imap_module',
                       '--without-mail_smtp_module',
#                       '--with-pcre='+os.path.join(os.environ['SROOT'],'lib'),
                       '--error-log-path=stderr',
                      ]
            if subprocess.call([os.path.join(nginx_dir,'configure'),
                                '--prefix='+dir_name]+options,
                                cwd=nginx_dir):
                raise Exception('nginx failed to configure')
            if subprocess.call(['make'],cwd=nginx_dir):
                raise Exception('nginx failed to make')
            if subprocess.call(['make','install'],cwd=nginx_dir):
                raise Exception('nginx failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
