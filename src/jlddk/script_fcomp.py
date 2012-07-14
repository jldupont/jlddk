"""
    Created on 2012-01-27
    @author: jldupont
"""
import os
import glob


def run(list_matches=None,
        list_diffs=None,
        list_sets=None,
        just_basename=None,
        just_filename=None,
        path_a=None,
        path_b=None,
        verbose=None
        ,**_
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
        
    if just_filename:
        ga=map(os.path.splitext, ga)
        ga=map(lambda t:t[0], ga)
        gb=map(os.path.splitext, gb)
        gb=map(lambda t:t[0], gb)
        
            
    sa=set(ga)
    sb=set(gb)
    
    if list_matches:
        out(sa.intersection(sb), verbose, '== ')
        
    if list_diffs:
        out(sa.symmetric_difference(sb), verbose, '!= ')
        
    if list_sets:
        out(sa, verbose, "pa: ")
        out(sb, verbose, "pb: ")

def out(liste, verbose, prefix):
    if not verbose:
        prefix=''
    for item in liste:
        print "%s%s" % (prefix, item)
    