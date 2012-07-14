"""
    Created on 2012-01-27
    @author: jldupont
"""
import sys, os, logging
from jlddk.tools_os import atomic_write, mkdir_p, touch

def run(
        path_dest=None
        ,append_ext=None
        ,disable_pass_through=False
        ,**_
        ):
    
    if append_ext is not None:
        append_ext=append_ext.strip(".'\"")
        logging.info("Using '%s' as extension" % append_ext)
    
    logging.info("Resolving destination path: %s" % path_dest)
    try:
        apath=os.path.abspath(path_dest)
        path=apath.strip("\"'")
        path=os.path.expanduser(os.path.expandvars(path))
    except:
        raise Exception("Can't resolve path")

    logging.info("Creating destination, if required...")
    mkdir_p(path_dest)

    ppid=os.getppid()        
    logging.info("Process pid: %s" % os.getpid())
    logging.info("Parent pid:  %s" % ppid)
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
        
        if not disable_pass_through:
            sys.stdout.write(iline+"\n")
            
        if append_ext is not None:
            filename=iline+".%s" % append_ext
        else:
            filename=iline
            
        path=os.path.join(path_dest, filename)
        
        code, _=touch(path)
        if not code.startswith("ok"):
            logging.error("Can't touch '%s'" % path)

            
        