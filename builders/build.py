#!/usr/bin/env python
"""Build the IceCube CVMFS repository on this OS.

Example:
  ./build.py --dest /cvmfs/icecube.opensciencegrid.org --src ../icecube.opensciencegrid.org
"""

import sys
import os

# append this directory to the path
if os.path.dirname(__file__) not in sys.path:
    sys.path.append(os.path.dirname(__file__))

def get_module(name, class_name='build'):
    """Import module"""
    x = __import__(name,globals(),locals(),[class_name])
    return (getattr(x,class_name))

def get_variants():
    build_variants = {}
    for module in os.listdir(os.path.join(os.path.dirname(__file__),'variants')):
        if module.endswith('.py') and module != '__init__.py':
            tmp = os.path.splitext(module)[0]
            build_variants[tmp] = get_module('variants.'+tmp)
    return build_variants

def absolute(p):
    return os.path.abspath(os.path.expandvars(os.path.expanduser(p)))

def main():
    from optparse import OptionParser
    
    parser = OptionParser()
    parser.add_option("--dest", type="string", default=None, 
                      help="CVMFS repository destination (inside repo)")
    parser.add_option("--src", type="string", default=None, 
                      help="Source for repository template")
    parser.add_option("--variant", type="string", default=None, 
                      help="Specific variant to build")
    
    (options, args) = parser.parse_args()
    
    build_variants = get_variants()
    
    options.dest = absolute(options.dest)
    options.src = absolute(options.src)
    
    if not options.variant:
        for v in build_variants:
            build_variants[v](src=options.src, dest=options.dest)
    elif options.variant in build_variants:
        build_variants[options.variant](src=options.src, dest=options.dest)
    else:
        raise Exception('variant %s not found'%(str(options.variant)))

if __name__ == '__main__':
    main()
