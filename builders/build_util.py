# build utilities

import os
import subprocess
import tempfile
import shutil

def wget(src, dest):
    if subprocess.call(['wget','-nv','-t','5','-O',dest,src]):
        raise Exception('wget failed: %s %s'%(src,dest))

def wget_recursive(src, dest):
    if subprocess.call(['wget','-nv','-N','-t','5','-P',dest,'-r','-l','1','-A','*.i3*','-nd',src]):
        raise Exception('wget_recursive failed: %s %s'%(src,dest))

def rsync(src,dest,flags='-a'):
    cmd = ['rsync']
    if flags:
        cmd.extend(flags)
    cmd += [src,dest]
    if subprocess.call(cmd):
        raise Exception('rsync failed: %s'%' '.join(cmd))

def unpack(src,dest,flags=['-zx']):
    cmd = ['tar']
    if flags:
        cmd.extend(flags)
    cmd += ['-f',src,'-C',dest]
    if subprocess.call(cmd):
        raise Exception('unpack failed: %s'%' '.join(cmd))

def get_md5sum(path):
    try:
        import hashlib
        digest = hashlib.md5()
    except ImportError:
        import md5
        digest = md5.new()

    filed = open(path)
    buffer = filed.read(16384)
    while buffer:
        digest.update(buffer)
        buffer = filed.read(16384)
    filed.close()
    return digest.hexdigest()

def check_md5sum(path,md5sum=''):
    name = os.path.basename(path)
    cur_sum = get_md5sum(path)
    if cur_sum == md5sum:
        return
    if os.path.exists(md5sum):
        for line in open(md5sum):
            line = line.strip()
            if line:
                parts = line.split(' ')
                if name == parts[-1] and cur_sum == parts[0]:
                    return
    raise Exception('md5sum doesn\'t match')

def copy_src(src,dest):
    """Copy anything from src to dest"""
    try:
        os.makedirs(dest)
    except Exception:
        pass
    for p in os.listdir(src):
        path = os.path.join(src,p)
        if os.path.isdir(path):
            copy_src(path,os.path.join(dest,p))
        else:
            shutil.copy2(path,dest)
