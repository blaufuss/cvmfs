#!/usr/bin/env python

import sys
import os
import subprocess
import json
from contextlib import contextmanager

class Publish(object):
    """Publish changes in a repository to cvmfs"""
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
    
    def publish(self):
        if not self.input or not self.output:
            self.getconf()
        
        if not os.path.isdir(self.input):
            raise Exception('input directory not valid')
        if not os.path.isdir(self.output):
            raise Exception('output directory not valid')
        
        with self._cvmfs_transaction():
            
            # TODO: add versioning
            
            subprocess.check_call(['/usr/bin/rsync','-og','-i','-rlptD',
                                   '--exclude /.cvmfscatalog','--delete',
                                   self.input,self.output])
        
    
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
