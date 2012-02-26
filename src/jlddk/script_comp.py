"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, sys, json, os
from time import sleep
from tools_os import get_root_files
from tools_os import resolve_path
from tools_logging import setloglevel
from tools_func import doOnTransition, transition_manager
from tools_misc import check_if_ok
from tools_func import check_transition
from tools_sys import BrokenPipe

from pyfnc import patterned, pattern, partial

def ilog(path):
    logging.info("Files accessible on path: %s" % path)
    
def wlog(path):
    logging.warning("Can't retrieve files from path: %s" % path)

def stdoutf():
    sys.stdout.flush()
    
def stdout(jo):
    try:    sys.stdout.write(json.dumps(jo)+"\n")
    except: 
        raise BrokenPipe("...broken pipe")

def run(primary_path=None, compare_path=None, 
        status_filename=None, check_path=None
        ,just_basename=None
        ,topic_name=None
        ,wait_status=None, polling_interval=None
        ,loglevel="info", logconfig=None):

    if logconfig is not None:
        logging.config.fileConfig(logconfig)

    setloglevel(loglevel)

    if check_path is not None:
        ct=check_transition()

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

    ### context for logging etc.
    ctx={
         "pp": primary_path
         ,"cp": compare_path
         ,"sp": status_path
         
         ,"pp_log" :{"up":    partial(ilog, primary_path)
                     ,"down":  partial(wlog, primary_path)
                     }
         ,"cp_log" :{"up":    partial(ilog, compare_path)
                     ,"down":  partial(wlog, compare_path)
                     }
         ,"topic_name": topic_name
         }

    ctx["tm"]=transition_manager(ctx)
    
    ppid=os.getppid()        
    logging.info("Process pid: %s" % os.getpid())
    logging.info("Parent pid: %s" % ppid)
    logging.info("Starting loop...")
    while True:
        if os.getppid()!=ppid:
            logging.warning("Parent terminated... exiting")
            break
            
        if check_path is not None:
            try:    exists=os.path.exists(check_path)
            except: exists=False
            
            maybe_tr, _=ct.send(exists)
            if maybe_tr=="tr" and exists:
                logging.info("Check path: passed")
            if maybe_tr=="tr" and not exists:
                logging.info("Check path: failed - skipping")
        else:
            ## fake 'exists'
            exists=True

        if exists:            
            code, msg=check_if_ok(status_path, default="ok")
            maybe_process(ctx, code, msg, primary_path, compare_path, just_basename)
        
        logging.debug("...sleeping for %s seconds" % polling_interval)
        sleep(polling_interval)



@pattern(dict, "ok", any, str, str, any)
def maybe_process_ok(ctx, _ok, _, primary_path, compare_path, just_basename):
    
    ### log rate limiter helper -- need to update status in context 'ctx'
    doOnTransition(ctx, "status_file.contents", "down", True, None)
    
    codep, primary_files=get_root_files(primary_path, strip_dirname=True)
    codec, compare_files=get_root_files(compare_path, strip_dirname=True)
    
    ### output some log info on transitions
    tm=ctx["tm"]
    tm.send(("pp_log", codep=="ok"))
    tm.send(("cp_log", codec=="ok"))
    
    ### not much to do if either path isn't accessible...
    if not codep.startswith("ok") or not codec.startswith("ok"):
        return
    
    if just_basename:
        pfiles=map(os.path.basename, primary_files)
        cfiles=map(os.path.basename, compare_files)
    else:
        pfiles=primary_files
        cfiles=compare_files
    
    try:
        setpf=set(pfiles)
        setcf=set(cfiles)
        common=setpf.intersection(setcf)
        
        
        
        diff={
               "pp":     primary_path
              ,"cp":     compare_path
              ,"pp-cp":  list(setpf-setcf)
              ,"cp-pp":  list(setcf-setpf)
              ,"common": list(common)
              }
        
        topic_name=ctx["topic_name"]
        if topic_name is not None:
            diff["topic"]=topic_name
        
        stdout(diff)
        stdoutf()
    except Exception, e:
        logging.error("Can't compute diff between paths: %s" % str(e))

@pattern(dict, any, str, any, any, any)
def maybe_process_nok(ctx, _nok, msg, _x, _y, _bn):
    """
    Rate limit logs
    """
    def wlog():
        logging.warning("Can't retrieve file contents from: %s" % ctx["sp"])
         
    doOnTransition(ctx, "status_file.contents", "down", False, wlog)


@patterned
def maybe_process(ctx, code, msg, primary_path, compare_path, just_basename): pass

        
        
        

