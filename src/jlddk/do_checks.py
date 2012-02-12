"""
    Created on 2012-01-19
    @author: jldupont
"""

try:
    import argparse
except:
    raise Exception("* package 'argparse' is necessary - get it from Pypi\n")


try:
    import pyinotify
except:
    raise Exception("* package 'pyinotify' required - get it from Pypi\n" )

try:
    import pyfnc
except:
    raise Exception("* package 'pyfnc' required - get it from Pypi\n" )
