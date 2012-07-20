#!/usr/bin/env python
"""
    Jean-Lou Dupont's general web related scripts/robots
    
    Created on 2012-01-19
    @author: jldupont
"""
__author__  ="Jean-Lou Dupont"
__version__ ="0.6.5"


from distutils.core import setup
from setuptools import find_packages

DESC="""
Overview
--------

This package contains a collection of 'robots'.
Each 'robot' is implemented with logging on stderr and processing result is output on stdout as either string or JSON.

Robots
------

* jldstrpkg: stdin --> formatter --> stdout
* jldwebscraper : extract anchor links from a web page
* jldfilter : filter stdin through a Python module, output on stdout
* jldcomp : compare 2 filesystem paths for difference in files
* jldfcomp : compare globs of files
* jldcat: 'cat' files to stdout, 1 per line with format 'filename\tcontents\n'
* jlduncat: Receive from stdin "key\tcontents\n" and write to key[.ext]
* jldjsoncat : 'cat' files to stdout by encapsulating them in JSON objects
* jldwebdl : gated web page download, source links contained in file system path
* jldinotify : path change notification over JSON/stdout
* jldfetcher : web page fetcher which takes instructions from stdin
* jldfilelist : list path files using include/exclude filter, JSON/stdout output
* jldclock : 1 second interval clock with min,hour,day markers
* jldpclean : kills processes left to pid=1
* jldtaskctl : task controller
* jldostr : outputs a string on stdout @ regular interval, pass-through for stdin-->stdout
* jldstatsubdirs: periodic status information on sub-dirs of path (JSON output & pass-through stdin-->stdout)
* jlddebouncer: debounces {key:value} pairs (JSON output & pass-through stdin-->stdout)
* jldrun : periodically run a python callable
* jldtouch: receive filename from stdin, 'touch' filename in destination path
* jldsplitter: a semi customizable file splitter

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
                     'src/scripts/jldcat',
                     'src/scripts/jlduncat',
                     'src/scripts/jldjsoncat',
                     'src/scripts/jldcomp',
                     'src/scripts/jldfcomp',
                     'src/scripts/jldinotify',
                     'src/scripts/jldfetcher',
                     'src/scripts/jldfilelist',
                     'src/scripts/jldclock',
                     'src/scripts/jldpclean',
                     'src/scripts/jldtaskctl',
                     'src/scripts/jldostr',
                     'src/scripts/jldstatsubdirs',
                     'src/scripts/jlddebouncer',
                     'src/scripts/jldrun',
                     'src/scripts/jldtouch',
                     ],                     
      zip_safe=False
      ,install_requires=["pyfnc >= 0.1.0"
                         ,"psutil"
                         ,"pyinotify"
                         ]
      ,long_description=DESC
      )

#############################################

f=open("latest", "w")
f.write(str(__version__)+"\n")
f.close()
