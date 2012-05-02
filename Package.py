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
Example of use :

    >>> from Package import Package
    >>> deluge = Package("deluge")
    >>> deluge.dependencies
    ['pygtk', 'boost', 'pyxdg', 'dbus-python', 'librsvg', 'desktop-file-utils', 'hicolor-icon-theme']
    >>> deluge.optional_dependencies
    {}

    >>> pygtk = Package("pygtk")
    >>> pygtk.dependencies
    ['libglade', 'pycairo', 'pygobject', 'python-numeric', 'gtk2']
    >>> pygtk.optional_dependencies
    {'gtk2': 'libglade'}

gtk2 is already include in libglade, the dependency gtk2 is not useful.
This class can also parse a PKGBUILD.

    >>> eclipse = Package("/var/abs/extra/eclipse/PKGBUILD", pkgbuild=True)
    >>> eclipse.dependencies
    ['jdk', 'gtk2']

"""

import pygraphviz as pg
import logging
import re
import subprocess

class Package(object):
    """
    Object represent a package and this dependencies.

    There are two methods for construct a package :
     * by a PKGBUILD.
     * by the name of a package and this package will find dependencies into the
     pacman database.
    """

    def __init__(self, name, pkgbuild=False, local=True):
        """
        Create a package
        """
        self.__local = local

        if(pkgbuild):
            (name, dep) = self.__init_pkgbuild(name)
        else:
            dep = self.__init_program(name)

        logging.debug("Create package : " + name + " " + str(dep))

        # Name of the package
        self.__name = name
        # List of direct dependencies
        self.__dependencies = dep
        # List of dependencies already included by another direct dependence
        self.__optional_dependencies = None
        # Tree of all dependencies
        self.__tree = None

    def __init_pkgbuild(self, name):
        """
        Parse a PKGBILD for create a package
        """
        pkgbuild = "".join(open(name, "r").readlines())
        pkgname_pattern = r"pkgname=([a-z\-_]*)"
        depends_pattern = r"depends=\(([^\)]*)\)"

        pkgname = re.findall(pkgname_pattern, pkgbuild)[0]
        dep = [d.split(">")[0]
               for d in re.findall(depends_pattern, pkgbuild)[0].
                               replace("\"", "").
                               replace("\'", "").
                               split()]

        return (pkgname, dep)

    def __init_program(self, name):
        """
        Use pacman -Qi (or -Si) for create package
        """
        if self.__local:
            args = ("pacman", "-Qi", name)
        else:
            args = ("pacman", "-Si", name)
        env = {}
        env["LANG"] = ""
        env["LC_ALL"] = ""
        pac = subprocess.Popen(args,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               env=env)
        raw = pac.stdout.read()

        if(len(raw)==0):
            dep = []
        else:
            dep = [d.split(">")[0]
                   for d in raw.split("Depends On")[1].
                                split("Optional Deps")[0].
                                split()[1:]]
            if(dep[0]=="None"):
                dep = []

        return dep

    def __tree_dependencies(self):
        """
        Construct complete dependence's tree for this package and store it
        """
        logging.debug("Generate tree dependencies")

        if(self.__tree != None):
            return self.__tree

        tree = pg.AGraph(directed=True)
        pile = []
        dico = {}
        pile.append(self)
        while(len(pile)>0):
            current = pile.pop()
            dico[current.__str__()] = current
            for dep_name in current.dependencies:
                if not dico.has_key(dep_name):
                    dep = Package(dep_name)
                    if(len(dep.dependencies)>0):
                        pile.append(dep)
                    tree.add_edge(current, dep)
                else:
                    tree.add_edge(current, dico[dep_name])
        self.__tree = tree
        return tree

    def draw(self, path=None):
        """
        Draw the dependece's tree
        """
        logging.debug("Draw graph")

        tree = self.__tree_dependencies()
        tree.layout(prog='dot')
        if(path==None):
            tree.draw("%s.png" % (self.__name))
        else:
            tree.draw(path)

    def __str__(self):
        return self.__name

    def __eq__(self, other):
        return self.__name == other.__str__()

    def _get_optional_dependencies(self):
        """
        Generate and return the optional dependencies list
        """
        logging.debug("Generate optional dependencies list")

        if self.__optional_dependencies:
            return self.__optional_dependencies

        dep = self.__dependencies
        tree = self.__tree_dependencies().copy()

        opt = [d
               for d in dep
               if len(tree.predecessors(d))>1]

        dico = {}
        for current in opt:
            tree.delete_edge(self, current)
            stack = [current]
            while(len(stack)>0):
                predecessors = tree.predecessors(stack.pop())
                tmp = [x
                       for x in dep
                       if x in predecessors]
                if(len(tmp)>0):
                    dico[current] = tmp[0]
                    break
                else:
                    stack += predecessors

        self.__optional_dependencies = dico
        return dico

    def _get_dependencies(self):
        """
        Return the dependencies of the package
        """
        return self.__dependencies

    dependencies = property(_get_dependencies, None, None, None)
    optional_dependencies = property(_get_optional_dependencies, None, None, None)
