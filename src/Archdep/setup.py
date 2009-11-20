#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='ArchDep',
      version='0.1',
      description='Check useful dependences in PKGBUILD or from package name.',
      author='Clément DEMOULINS',
      author_email='cdemoulins@gmail.com',
      url='http://trac2.assembla.com/cdemoulins/browser/Python/src/ArchDep/',
      py_modules=['Package'],
      license='GNU GPL 3',
      scripts=['archdep.py'],
     )
