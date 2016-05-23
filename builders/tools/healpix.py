"""healpix build/install"""

import os
import subprocess
import tempfile
import shutil
import glob

from build_util import wget, unpack, version_dict

def install(dir_name,version=None,i3ports=False,for_clang=False):
    if not os.path.exists(os.path.join(dir_name,'lib','libhealpix_cxx.so')):
        print('installing healpix version',version)
        try:
            tmp_dir = tempfile.mkdtemp()
            name = 'README'
            path = os.path.join(tmp_dir,name)
            url = os.path.join('http://iweb.dl.sourceforge.net/project/healpix/Healpix_'+version,name)
            wget(url,path)
            for line in open(path):
                if 'tar.gz' in line:
                    name = line.strip().strip(':')
                    break
            else:
                raise Exception('healpix: cannot determine tarball name')
            print 'NAME:',name
            url = os.path.join('http://iweb.dl.sourceforge.net/project/healpix/Healpix_'+version,name)
            # the sourceforge retry
            wget(url,path,retry=5)
            unpack(path,tmp_dir)

            # make C healpix
            healpix_dir = os.path.join(tmp_dir,'Healpix_'+version,'src','C','subs')
            if i3ports:
                i3ports_dir = os.environ['I3_PORTS']
            else:
                i3ports_dir = dir_name
            if subprocess.call(['make','shared',
                                'CFITSIO_INCDIR='+os.path.join(i3ports_dir,'include'),
                                'CFITSIO_LIBDIR='+os.path.join(i3ports_dir,'lib')
                               ],cwd=healpix_dir):
                raise Exception('healpix C failed to make')
            if subprocess.call(['make','install',
                                'INCDIR='+os.path.join(dir_name,'include'),
                                'LIBDIR='+os.path.join(dir_name,'lib')
                               ],cwd=healpix_dir):
                raise Exception('healpix C failed to install')

            # special environ
            env = dict(os.environ)
            if for_clang:
                env['CFLAGS'] = '-fPIC'
                env['CPPFLAGS'] = '-fPIC'
                env['LDFLAGS'] = '-lgcc_s' # the gfortran we use when installing clang seems to need this
            else:
                env['CFLAGS'] = '-fno-tree-fre -fPIC'
                env['CPPFLAGS'] = '-fno-tree-fre -fPIC'

            # make CXX healpix
            healpix_dir = os.path.join(tmp_dir,'Healpix_'+version,'src','cxx')
            if subprocess.call(['autoconf'],cwd=healpix_dir):
                raise Exception('healpix CXX failed to autoconf')
            if subprocess.call([os.path.join(healpix_dir,'configure'),
                                '--prefix='+dir_name,'--disable-openmp',
                                '--with-libcfitsio='+dir_name,
                                '--with-libcfitsio-include='+os.path.join(i3ports_dir,'include'),
                                '--with-libcfitsio-lib='+os.path.join(i3ports_dir,'lib'),
                               ],cwd=healpix_dir,env=env):
                raise Exception('healpix CXX failed to configure')
            conf = os.path.join(healpix_dir,'config','config.auto')
            data = open(conf).read().replace('-march=native','').replace('-ffast-math','')
            open(conf,'w').write(data)
            if subprocess.call(['make'], cwd=healpix_dir):
                raise Exception('healpix CXX failed to make')
            lib_dir = os.path.join(healpix_dir,'auto','lib')
            link_cmd = ['gcc', '-shared', '-o',
                        os.path.join(lib_dir, 'libhealpix_cxx.so'),
                        '-L'+os.path.join(i3ports_dir,'lib'),'-lcfitsio',
                        '-Wl,--whole-archive']
            link_cmd += glob.glob(os.path.join(lib_dir, '*.a'))
            link_cmd += ['-Wl,--no-whole-archive']
            if subprocess.call(link_cmd, cwd=healpix_dir):
                raise Exception('healpix CXX failed to link')
            for root,dirs,files in os.walk(os.path.join(healpix_dir,'auto')):
                install_cmd = ['install','-D']
                p = os.path.basename(root)
                if 'include' in root:
                    install_cmd.extend(['-m','644'])
                    p = os.path.join(p,'healpix_cxx')
                for f in files:
                    if f.endswith('.a'):
                        continue
                    if subprocess.call(install_cmd + [os.path.join(root,f),
                                       os.path.join(dir_name,p,f)]
                                       ,cwd=healpix_dir):
                        raise Exception('healpix CXX failed to install %s'%os.path.join(root,f))
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
