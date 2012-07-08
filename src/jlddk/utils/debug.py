"""
    Created on 2012-07-08
    @author: jldupont
"""
import sys

def echo(line):
    print line

def null(line):
    pass

def dump_stderr(line):
    sys.stderr.write(line)
    sys.stderr.flush()
