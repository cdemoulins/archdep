#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import OptionParser
import logging
from Package import Package

def main():
    """
    Program main function. 
    """
    
    parser = OptionParser()
    parser.add_option("-g", "--draw", action="store_true", default=False,
                      help="Draw the dependence's tree")
    parser.add_option("-p", "--program", action="store_true", default=False,
                      help="Calcul optional dependences for a program and not" \
                      + " a PKGBUILD")
    parser.add_option("-r", "--request", action="store_true", default=False,
                      help="Question the remote database (pacman -Si)," \
                      + " default is local (pacman -Qi)")
    parser.add_option("-d", "--debug", action="store_true", default=False,
                      help="Add debug messages")

    (options, args) = parser.parse_args()
    
    if(len(args) == 0):
        parser.print_help()
        return 1
    
    if(options.debug):
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s - %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S')
    
    for arg in args:
        package = Package(arg, not options.program, not options.request)
        if(options.draw):
            package.draw()
        for dep in package.optional_dependences:
            print "%s is already include by %s" % (dep, package.optional_dependences[dep])

if __name__ == '__main__':
    main()