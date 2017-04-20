"""pythia6 build/install"""

import os
import subprocess
import tempfile
import shutil
from glob import glob

from build_util import wget, unpack, version_dict, get_fortran_compiler, cpu_cores

makefile = """
all: lib-shared
lib-shared: libPythia6.so

tpythia6_called_from_cc.o:
	$(FC) $(FFLAGS) -fno-second-underscore -c tpythia6_called_from_cc.F

libPythia6.so: main.o pythia6_common_address.o pythia%s.o tpythia6_called_from_cc.o pythia6_rng_callback.o
	$(FC) -shared -Wl,-soname,libPythia6.so -o libPythia6.so $+

install: libPythia6.so
	install -m 755 -d $(PREFIX)/lib
	install -m 644 $+ $(PREFIX)/lib
"""

pythia6_rng_callback_c = """
/* forward decl, original Pythia impl */
extern double old_pyr_(int* idummy);

/* function pointer contating the current impl */
double (*pyr_callback)(int*) = 0;

/* setter for the pyr callback */
void set_pyr_callback(double (*new_callback)(int*) )
{
  pyr_callback = new_callback;
}

/* call the current PYR implementation */
double ext_pyr_(int* idummy)
{
  if (pyr_callback)
  {
    return (*pyr_callback)(idummy);
  }
  else
  {
    return old_pyr_(idummy);
  }
}
"""

main_c = 'void MAIN__() {}'

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'lib','libPythia6.so')):
        print('installing pythia6 version',version)
        name = 'pythia'+version.replace('.','')+'.f'
        try:
            tmp_dir = tempfile.mkdtemp()
            root_name = 'pythia6'
            root_path = os.path.join(tmp_dir,'pythia6.tar.gz')
            root_url = 'https://root.cern.ch/download/pythia6.tar.gz'
            wget(root_url,root_path)
            unpack(root_path,tmp_dir)
            build_dir = os.path.join(tmp_dir,root_name)
            for g in glob(os.path.join(build_dir,'pythia*.f')):
                os.remove(g)
            path = os.path.join(build_dir,name)
            url = os.path.join('http://home.thep.lu.se/~torbjorn/pythia6/',name)
            wget(url,path)
            with open(os.path.join(build_dir,'Makefile'),'w') as f:
                f.write(makefile%(version.replace('.',''),))
            with open(os.path.join(build_dir,'pythia6_rng_callback.c'),'w') as f:
                f.write(pythia6_rng_callback_c)
            with open(os.path.join(build_dir,'main.c'),'w') as f:
                f.write(main_c)
            mod_env = dict(os.environ)
            mod_env['PREFIX'] = dir_name
            mod_env['CFLAGS'] = '-m64 -fPIC'
            mod_env['FFLAGS'] = '-m64 -fPIC'
            mod_env['FC'] = get_fortran_compiler()
            if subprocess.call(['make','-j',cpu_cores], cwd=build_dir, env=mod_env):
                raise Exception('pythia6 failed to make')
            if subprocess.call(['make','install'], cwd=build_dir,
                               env=mod_env):
                raise Exception('pythia6 failed to install')
        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
