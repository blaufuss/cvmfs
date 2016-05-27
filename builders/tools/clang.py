"""clang build/install"""

import os
import subprocess
import tempfile
import shutil
import copy

from build_util import wget, unpack_xz, version_dict

try:
    import multiprocessing
    cpu_cores = multiprocessing.cpu_count()
except ImportError:
    cpu_cores = 1

# Patch the driver so that it will, if left to its own devices, link against libc++ instead of libstdc++
# and will assume that this also requires linking with libc++abi
toolchain_patch = """
--- llvm/tools/clang/lib/Driver/ToolChain.cpp.orig      2016-05-22 17:33:26.000000000 -0500
+++ llvm/tools/clang/lib/Driver/ToolChain.cpp   2016-05-22 17:35:24.000000000 -0500
@@ -544,7 +544,7 @@
       << A->getAsString(Args);
   }

-  return ToolChain::CST_Libstdcxx;
+  return ToolChain::CST_Libcxx;
 }

 /// \brief Utility function to add a system include directory to CC1 arguments.
@@ -608,6 +608,7 @@
   switch (Type) {
   case ToolChain::CST_Libcxx:
     CmdArgs.push_back("-lc++");
+    CmdArgs.push_back("-lc++abi"); //not fully general, but good enough
     break;

   case ToolChain::CST_Libstdcxx:
"""

# The libc++ build system is hard coded to insist on linking against libgcc_s,
# but we plan to have a perfectly good libunwind which we would rather use.
cmakelists_patch_3_7 = """
Index: llvm/projects/libcxx/lib/CMakeLists.txt
===================================================================
--- llvm/projects/libcxx/lib/CMakeLists.txt     (revision 248365)
+++ llvm/projects/libcxx/lib/CMakeLists.txt     (working copy)
@@ -61,7 +61,7 @@
 append_if(libraries LIBCXX_HAS_C_LIB c)
 append_if(libraries LIBCXX_HAS_M_LIB m)
 append_if(libraries LIBCXX_HAS_RT_LIB rt)
-append_if(libraries LIBCXX_HAS_GCC_S_LIB gcc_s)
+append_if(libraries LIBCXX_HAS_GCC_S_LIB unwind)

 if (LIBCXX_COVERAGE_LIBRARY)
   target_link_libraries(cxx ${LIBCXX_COVERAGE_LIBRARY})
"""
cmakelists_patch = """
Index: llvm/projects/libcxx/lib/CMakeLists.txt
===================================================================
--- llvm/projects/libcxx/lib/CMakeLists.txt.orig        2015-12-16 17:41:05.000000000 -0600
+++ llvm/projects/libcxx/lib/CMakeLists.txt     2016-05-22 17:45:27.000000000 -0500
@@ -78,7 +78,7 @@
 add_library_flags_if(LIBCXX_HAS_C_LIB c)
 add_library_flags_if(LIBCXX_HAS_M_LIB m)
 add_library_flags_if(LIBCXX_HAS_RT_LIB rt)
-add_library_flags_if(LIBCXX_HAS_GCC_S_LIB gcc_s)
+add_library_flags_if(LIBCXX_HAS_GCC_S_LIB unwind)

 # Setup flags.
 add_flags_if_supported(-fPIC)
"""

# At the time of writing it's 2015. Let's at least turn on features from 2011 by default.
cxx11_patch = """
Index: llvm/tools/clang/lib/Driver/Tools.cpp
===================================================================
--- llvm/tools/clang/lib/Driver/Tools.cpp    (revision 248309)
+++ llvm/tools/clang/lib/Driver/Tools.cpp    (working copy)
@@ -3881,8 +3881,12 @@
     if (!types::isCXX(InputType))
       Args.AddAllArgsTranslated(CmdArgs, options::OPT_std_default_EQ, "-std=",
                                 /*Joined=*/true);
-    else if (IsWindowsMSVC)
-      ImplyVCPPCXXVer = true;
+    else{
+      if (IsWindowsMSVC)
+        ImplyVCPPCXXVer = true;
+      else
+        CmdArgs.push_back("-std=c++14");
+    }

     Args.AddLastArg(CmdArgs, options::OPT_ftrigraphs,
                     options::OPT_fno_trigraphs);
"""

def install(dir_name,version=None):
    if not os.path.exists(os.path.join(dir_name,'bin','clang')):
        print('installing clang version',version)

        main_url = os.path.join("http://llvm.org/releases", str(version))
        urls = [
            ('llvm-'+str(version)+'.src',              'llvm'),
            ('libcxx-'+str(version)+'.src',            'llvm/projects/libcxx'),
            ('libcxxabi-'+str(version)+'.src',         'llvm/projects/libcxxabi'),
            ('libunwind-'+str(version)+'.src',         'llvm/projects/libunwind'),
            ('compiler-rt-'+str(version)+'.src',       'llvm/projects/compiler-rt'),
            ('cfe-'+str(version)+'.src',               'llvm/tools/clang'),
            ('clang-tools-extra-'+str(version)+'.src', 'llvm/tools/clang/tools/extra'),
        ]

        try:
            tmp_dir = tempfile.mkdtemp()

            for entry in urls:
                name = entry[0]+'.tar.xz'
                url = os.path.join(main_url, name)
                download_path = os.path.join(tmp_dir, name)
                wget(url,download_path)
                unpack_xz(download_path,tmp_dir)
                extracted_dir = os.path.join(tmp_dir,entry[0])
                canonical_dir = os.path.join(tmp_dir,entry[1])
                os.rename(extracted_dir, canonical_dir)

            clang_dir = os.path.join(tmp_dir, urls[0][1])

            # Patch clang driver so that it will link products against libunwind instead of various gcc support libraries
            if subprocess.call(['sed',
                                '-i',
                                '-e','s@"-lgcc[^"]*"@"-lunwind"@g',
                                'tools/clang/lib/Driver/Tools.cpp'],cwd=clang_dir):
                raise Exception('clang could not be patched')

            if subprocess.call("echo '"+toolchain_patch+"' | patch -p1",cwd=clang_dir,shell=True):
                raise Exception('clang could not be patched')
            if version=="3.7.0":
                if subprocess.call("echo '"+cmakelists_patch_3_7+"' | patch -p1",cwd=clang_dir,shell=True):
                    raise Exception('clang could not be patched')
            else:
                if subprocess.call("echo '"+cmakelists_patch+"' | patch -p1",cwd=clang_dir,shell=True):
                    raise Exception('clang could not be patched')
            if subprocess.call("echo '"+cxx11_patch+"' | patch -p1",cwd=clang_dir,shell=True):
                raise Exception('clang could not be patched')

            # create an out-of-source build directory
            clang_build_dir = os.path.join(tmp_dir, 'llvm_build')
            if not os.path.exists(clang_build_dir):
                os.makedirs(clang_build_dir)

            if subprocess.call(['cmake', clang_dir,
                                '-DCMAKE_BUILD_TYPE=Release',
                                '-DLIBCXXABI_USE_LLVM_UNWINDER=True',
                                # '-DLLVM_TARGETS_TO_BUILD=X86',
                                '-DCMAKE_INSTALL_PREFIX='+dir_name,
                                ],cwd=clang_build_dir):
                raise Exception('clang cmake failed')

            if subprocess.call(['make','-j'+str(cpu_cores)],cwd=clang_build_dir):
                raise Exception('clang failed to make')
            if subprocess.call(['make','install'],cwd=clang_build_dir):
                raise Exception('clang failed to install')


        finally:
            shutil.rmtree(tmp_dir)

def versions():
    return version_dict(install)
