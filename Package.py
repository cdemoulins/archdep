# -*- coding: utf-8 -*-

"""
Example of use :

    >>> from Package import Package
    >>> deluge = Package("deluge")
    >>> deluge.dependences
    ['pygtk', 'boost', 'pyxdg', 'dbus-python', 'librsvg', 'desktop-file-utils', 'hicolor-icon-theme']
    >>> deluge.optional_dependences
    {}

    >>> pygtk = Package("pygtk")
    >>> pygtk.dependences
    ['libglade', 'pycairo', 'pygobject', 'python-numeric', 'gtk2']
    >>> pygtk.optional_dependences
    {'gtk2': 'libglade'}

gtk2 is already include in libglade, the dependence gtk2 is not useful.
This class can also parse a PKGBUILD.

    >>> eclipse = Package("/var/abs/extra/eclipse/PKGBUILD", pkgbuild=True)
    >>> eclipse.dependences
    ['jdk', 'gtk2']

"""

import pygraphviz as pg
import logging
import re
import subprocess

class Package(object):
    """
    Object represent a package and this dependences.
    
    There are two methods for construct a package :
     * by a PKGBUILD.
     * by the name of a package and this package will find dependences into the
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
        # List of direct dependences
        self.__dependences = dep
        # List of dependences already included by another direct dependence 
        self.__optional_dependences = None
        # Tree of all dependences
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
    
    def __tree_dependences(self):
        """
        Construct complete dependence's tree for this package and store it
        """
        logging.debug("Generate tree dependences")
        
        if(self.__tree != None):
            return self.__tree
        
        tree = pg.AGraph(directed=True)
        pile = []
        dico = {}
        pile.append(self)
        while(len(pile)>0):
            current = pile.pop()
            dico[current.__str__()] = current
            for dep_name in current.dependences:
                if not dico.has_key(dep_name):
                    dep = Package(dep_name)
                    if(len(dep.dependences)>0):
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
        
        tree = self.__tree_dependences()
        tree.layout(prog='dot')
        if(path==None):
            tree.draw("%s.png" % (self.__name))
        else:
            tree.draw(path)
    
    def __str__(self):
        return self.__name

    def __eq__(self, other):
        return self.__name == other.__str__()

    def _get_optional_dependences(self):
        logging.debug("Generate optional dependences list")
        
        if self.__optional_dependences:
            return self.__optional_dependences
        
        dep = self.__dependences
        tree = self.__tree_dependences().copy()
        
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
        
        self.__optional_dependences = dico
        return dico

    def _get_dependences(self):
        return self.__dependences

    dependences = property(_get_dependences, None, None, None)
    optional_dependences = property(_get_optional_dependences, None, None, None)
