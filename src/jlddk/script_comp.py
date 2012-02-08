"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, sys, json, os
from time import sleep
from tools_os import get_root_files, file_contents
from tools_os import rm, can_write, resolve_path
from tools_logging import setloglevel
from tools_func import check_transition, coroutine, doOnTransition
from tools_misc import check_if_ok

from pyfnc import patterned, pattern

def stdout(jo):
    try:    sys.stdout.write(json.dumps(jo)+"\n")
    except: pass

def maybe_get_status(filepath):
    if filepath:
        return file_contents(filepath)
    return ("ok", None)

def run(primary_path=None, compare_path=None, status_filename=None
        ,wait_status=None, polling_interval=None
        ,loglevel="info", logconfig=None):

    if logconfig is not None:
        logging.config.fileConfig(logconfig)

    setloglevel(loglevel)

    code, primary_path=resolve_path(primary_path)
    if not code.startswith("ok"):
        raise Exception("can't resolve primary path '%s'" % primary_path)
    
    code, compare_path=resolve_path(compare_path)
    if not code.startswith("ok"):
        raise Exception("can't resolve compare path '%s'" % compare_path)
            
    if wait_status:
        status_path=os.path.join(primary_path, status_filename)
        logging.info("Using status file path: %s" % status_path)
    else: 
        status_path=None

    ctx={
         "pp": primary_path
         ,"cp": compare_path
         ,"sp": status_path
         }
            
    logging.info("Starting loop...")
    while True:
        
        code, msg=check_if_ok(status_path, default="ok")
        maybe_process(ctx, code, msg, primary_path, compare_path)
        
        logging.debug("...sleeping for %s seconds" % polling_interval)
        sleep(polling_interval)



@pattern(dict, "ok", any, str, str)
def maybe_process_ok(ctx, _ok, _, primary_path, compare_path):
    
    ### log rate limiter helper -- need to update status in context 'ctx'
    doOnTransition(ctx, "status_file.contents", "down", True, None)
    

@pattern(dict, any, str, any, any)
def maybe_process_nok(ctx, _nok, msg, _x, _y):
    """
    Rate limit logs
    """
    def wlog():
        logging.warning("Can't retrieve file contents from: %s" % ctx["sp"])
         
    doOnTransition(ctx, "status_file.contents", "down", False, wlog)

    

@patterned
def maybe_process(ctx, code, msg, primary_path, compare_path): pass

        
        
        

