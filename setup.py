#!/usr/bin/env python
"""
    Jean-Lou Dupont's general web related scripts/robots
    
    Created on 2012-01-19
    @author: jldupont
"""
__author__  ="Jean-Lou Dupont"
__version__ ="0.1.2"


from distutils.core import setup
from setuptools import find_packages

DESC="""
Overview
--------

This package contains a collection of 'robots'.
Each 'robot' is implemented with logging on stderr and processing result is output on stdout as either string or JSON.

Configuration
-------------

Can be performed through options on the command line or using a file (use a leading `@`).
"""

setup(name=         'jlddk',
      version=      __version__,
      description=  'Collection of robots',
      author=       __author__,
      author_email= 'jl@jldupont.com',
      url=          'http://www.systemical.com/doc/opensource/jlddk',
      package_dir=  {'': "src",},
      packages=     find_packages("src"),
      scripts=      ['src/scripts/jldwebscraper',
                     'src/scripts/jldfilter',
                     'src/scripts/jldwebdl',
                     ],
      package_data = {
                      '':[ "*.gif", "*.png", "*.jpg" ],
                      },
      include_package_data=True,                      
      zip_safe=False
      ,long_description=DESC
      )
