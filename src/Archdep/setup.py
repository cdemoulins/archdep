#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='ArchDep',
      version='0.1',
      description='Check redundant dependences in PKGBUILD or from package name.',
      author='Clément DEMOULINS',
      author_email='cdemoulins@gmail.com',
      url='https://indefero.archivel.fr/index.php/p/archdep',
      py_modules=['Package'],
      license='GNU GPL 3',
      scripts=['archdep.py'],
     )
