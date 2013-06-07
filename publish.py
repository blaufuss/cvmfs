#!/usr/bin/env python

import sys
import os
import subprocess
import json
from contextlib import contextmanager

class Publish(object):
    """Publish changes in a repository to cvmfs"""
    data_dir = 'data'
    ports_dir = 'ports'
    meta_dir = 'meta-projects'
    
    def __init__(self,input=None,output=None,config=None):
        self.input = input
        self.output = output
        self.config = config
    
    def getconf(self):
        conf = json.load(open(self.config))
        self.input = conf['input']
        self.output = conf['output']
    
    @contextmanager
    def _cvmfs_transaction(self):
        subprocess.check_call(['/usr/bin/sudo','/usr/bin/cvmfs_server',
                               'transaction'])
        try:
            yield
        except:
            subprocess.check_call(['/usr/bin/sudo','/usr/bin/cvmfs_server',
                                   'abort'])
        else:
            subprocess.check_call(['/usr/bin/sudo','/usr/bin/cvmfs_server',
                                   'publish'])
    
    def _publish_with_versioning(self,input_dir,output_dir):
        """Do versioning of directory"""
        version = 0
        for d in os.listdir(output_dir):
            if d.startswith('v'):
                v = int(d[1:])
                if v > version:
                    version = v
        version = 'v%06d'%version
        
        subprocess.check_call(['/usr/bin/rsync','-og','-i','-rlptD',
                               '--exclude /.cvmfscatalog','--delete',
                               input_dir,os.path.join(output_dir,version)])
        
        # symlink latest to the new version
        curdir = os.getcwd()
        try:
            os.chdir(output_dir)
            os.remove('latest')
            os.symlink(version,'latest')
        finally:
            os.chdir(curdir)
    
    def _publish_data(self):
        """Do versioning and copying of data"""
        input_data = os.path.join(self.input,self.data_dir)
        output_data = os.path.join(self.output,self.data_dir)
        self._publish_with_versioning(input_data,output_data)
    
    def _publish_ports(self,arch):
        """Do versioning and copying of ports"""
        input_data = os.path.join(self.input,self.ports_dir)
        output_data = os.path.join(self.output,self.ports_dir)
        self._publish_with_versioning(input_data,output_data)
    
    def _publish_meta(self,arch):
        """Do copying of meta-projects"""
        input_dir = os.path.join(self.input,self.meta_dir)
        output_dir = os.path.join(self.output,self.meta_dir)
        
        subprocess.check_call(['/usr/bin/rsync','-og','-i','-rlptD',
                               '--exclude /.cvmfscatalog','--delete',
                               input_dir,output_dir])
    
    def publish(self):
        """Publish a repository"""
        if not self.input or not self.output:
            self.getconf()
        
        if not os.path.isdir(self.input):
            raise Exception('input directory not valid')
        if not os.path.isdir(self.output):
            raise Exception('output directory not valid')
        
        with self._cvmfs_transaction():
            
            for d in os.listdir(self.input):
                if d == 'data':
                    continue
                elif os.path.isdir(d):
                    # must be an ARCH
                    self._publish_ports(d)
                    self._publish_meta(d)
                else:
                    # random file
                    subprocess.check_call([
                        '/usr/bin/rsync','-og','-i','-rlptD',
                        '--exclude /.cvmfscatalog','--delete',
                        os.path.join(self.input,d),
                        os.path.join(self.output,d)])
            
            self._publish_data()
        
    
if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-i', '--input', dest='input',
                      type='string', default=None,
                      help='input directory')
    parser.add_option('-o', '--output', dest='output',
                      type='string', default=None,
                      help='output directory')
    parser.add_option('-c', '--config', dest='config',
                      type='string', default='config.json',
                      help='config file')
    (options, args) = parser.parse_args()
    
    p = Publish(input=options.input,
                output=options.output,
                config=options.config)
    p.publish()
