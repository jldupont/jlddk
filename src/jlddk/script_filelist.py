"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, sys, json, os
from time import sleep
from tools_os import get_root_files
from tools_os import resolve_path, filter_files_by_ext
from tools_misc import batch


def stdout(jo):
    try:    sys.stdout.write(json.dumps(jo)+"\n")
    except: pass

def run(path_source=None
        ,polling_interval=None
        ,ext_include=None
        ,ext_exclude=None
        ,batch_size=None
        ):

    if ext_include is not None and ext_exclude is not None:
        raise Exception("'ee' and 'ei' options are mutually exclusive")
    
    criteria="include" if ext_include else "exclude"
    elist=ext_include or ext_exclude

    code, path_source=resolve_path(path_source)
    if not code.startswith("ok"):
        raise Exception("can't resolve path '%s'" % path_source)

    logging.info("Process pid: %s" % os.getpid())
    ppid=os.getppid()
    logging.info("Parent pid: %s" % ppid)
    logging.info("Starting loop...")    
    while True:
        if os.getppid()!=ppid:
            logging.warning("Parent terminated... exiting")
            break
        
        code, files=get_root_files(path_source)
        l=filter_files_by_ext(criteria, elist, (code, files))
        
        if l:
            for bunch in batch(l, batch_size):
                output(path_source, bunch)
        
        logging.debug("...sleeping for %s seconds" % polling_interval)
        sleep(polling_interval)


def output(path_source, files):
    d={"files": files
       ,"path_source": path_source
       }
    stdout(d)