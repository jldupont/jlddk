"""
    Created on 2012-01-27
    @author: jldupont
"""
import sys, os, logging
from jlddk.tools_os import atomic_write

def maybe_log(verbose, msg):
    if verbose:
        logging.info(msg)
    

def run(path_dest=None,
        ignore_fault=False,
        verbose=False,
        ext=None
        ,keep_key=None
        ,**_
        ):
    
    maybe_log(verbose, "Resolving destination path: %s" % path_dest)
    try:
        apath=os.path.abspath(path_dest)
        path=apath.strip("\"'")
        path=os.path.expanduser(os.path.expandvars(path))
    except:
        raise Exception("Can't resolve path")

    ppid=os.getppid()        
    logging.info("Process pid: %s" % os.getpid())
    logging.info("Parent pid: %s" % ppid)
    logging.info("Starting loop...")
    while True:
        if os.getppid()!=ppid:
            logging.warning("Parent terminated... exiting")
            break
            
        try:
            iline=sys.stdin.readline().strip(" \n")
            if len(iline)==0:
                continue
        except:
            raise Exception("Exiting... probably broken pipe")
        
        try:
            key, contents=iline.split("\t", 1)
        except Exception, e:
            if not ignore_fault:
                raise Exception("Invalid input format: %s" % e)
            continue
        
        maybe_log(verbose, "Received input with key '%s'" % key)
        
        if ext is not None:
            dpath=os.path.join(path, key, ext)
        else:
            dpath=os.path.join(path, key)
            
        if keep_key:
            contents="%s\t%s" % (key, contents)
            
        maybe_log(verbose, "Writing to: %s" % dpath)
        result, _=atomic_write(dpath, contents)
        if not result.startswith("ok"):
            if not ignore_fault:
                raise Exception("Error writing output file '%s':%s" % (dpath, _))
        
        