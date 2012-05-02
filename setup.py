#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='ArchDep',
      version='0.1',
      description='Check redundant dependences in PKGBUILD or from package name.',
      author='Clément Démoulins',
      author_email='clement@archivel.fr',
      url='git://github.com/cdemoulins/archdep.git',
      py_modules=['Package'],
      license='GNU GPL 3',
      scripts=['archdep.py'],
     )
