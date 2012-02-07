"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, sys, json, os
from time import sleep
from tools_os import get_root_files, file_contents
from tools_os import rm, can_write, resolve_path
from tools_logging import setloglevel
from tools_func import check_transition, coroutine

def stdout(jo):
    try:    sys.stdout.write(json.dumps(jo)+"\n")
    except: pass

def maybe_get_status(filepath):
    if filepath:
        return file_contents(filepath)
    return ("ok", None)

def run(primary_path=None, compare_path=None, status_filename=None,
        wait_status=None,
        loglevel="info", logconfig=None, polling_interval=None):

    if logconfig is not None:
        logging.config.fileConfig(logconfig)

    setloglevel(loglevel)

    code, rp=resolve_path(primary_path)
    if not code.startswith("ok"):
        raise Exception("can't resolve primary path '%s'" % primary_path)
    primary_path=rp
    
    code, rp=resolve_path(compare_path)
    if not code.startswith("ok"):
        raise Exception("can't resolve compare path '%s'" % compare_path)
    compare_path=rp
            
    p1=l1(wait_status, status_filename, primary_path, compare_path)
            
    if wait_status:
        status_path=os.path.join(primary_path, status_filename)
        logging.info("Using status file path: %s" % status_path)
    else: 
        status_path=None
            
    logging.info("Starting loop...")
    while True:
        
        code, contents=maybe_get_status(status_path)
        if not code.startswith("ok"):
            pass
        
        logging.debug("...sleeping for %s seconds" % polling_interval)
        sleep(polling_interval)


@coroutine
def l1(wait_status, status_filename, primary_path, compare_path):
    
    while True:
        msg=(yield)

        code, primary_files=get_root_files(primary_path)
