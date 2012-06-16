"""
    Created on 2012-01-27
    @author: jldupont
"""
import sys
import os
import glob

from tools_os import get_root_files
from tools_os import resolve_path


def run(list_matches=None,
        list_diffs=None,
        just_basename=None,
        path_a=None,
        path_b=None,
        verbose=None
        ):

    try:
        ga=glob.glob(path_a)
    except:
        raise Exception("Pattern for path 'a' is invalid")

    try:
        gb=glob.glob(path_b)
    except:
        raise Exception("Pattern for path 'b' is invalid")
    

    if just_basename:
        ga=map(os.path.basename, ga)
        gb=map(os.path.basename, gb)
            
    sa=set(ga)
    sb=set(gb)
    
    if list_matches:
        out(sa.intersection(sb), verbose, '== ')
        
    if list_diffs:
        out(sa.symmetric_difference(sb), verbose, '!= ')
        

def out(liste, verbose, prefix):
    if not verbose:
        prefix=''
    for item in liste:
        print "%s%s" % (prefix, item)
    