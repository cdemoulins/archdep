#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Copyright © 2012 - Clément Démoulins <clement@archivel.fr>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Archdep script.
"""

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
    parser.add_option("-p", "--package-name", action="store_true",
            default=False, dest="package",
            help="Calcul optional dependences for a package name and not " \
                    + "a PKGBUILD")
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
            print "%s is already include by %s" % \
                    (dep, package.optional_dependences[dep])

if __name__ == '__main__':
    main()
