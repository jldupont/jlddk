"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, os
from time import sleep
from tools_os import get_root_files, mkdir_p, rmdir
from tools_os import resolve_path, touch
from tools_func import doOnTransition, transition_manager
from tools_misc import check_if_ok
from tools_func import check_transition
from tools_sys import stdoutf, stdoutj, stdout
from tools_logging import ilog, wlog

from pyfnc import patterned, pattern, partial



def run(primary_path=None, compare_path=None, 
        dest_path=None,
        status_filename=None, check_path=None
        ,just_basename=None
        ,topic_name=None
        ,exts=None
        ,wait_status=None, polling_interval=None
        ,just_zppp=None, just_ppzp=None, just_com=None
        ,**_):

    if check_path is not None:
        ct=check_transition()

    if dest_path:
        code, dest_path=resolve_path(dest_path)
        if not code.startswith("ok"):
            raise Exception("can't destination path '%s'" % dest_path)
        
        logging.info("Creating (if necessary) destination path: %s" % dest_path)
        code, msg=mkdir_p(dest_path)
        if code!="ok":
            raise Exception("Can't create path: %s" % dest_path)

    code, primary_path=resolve_path(primary_path)
    if not code.startswith("ok"):
        raise Exception("can't resolve primary path '%s'" % primary_path)
    
    logging.info("Creating (if necessary) primary path: %s" % primary_path)
    mkdir_p(primary_path)
    
    code, compare_path=resolve_path(compare_path)
    if not code.startswith("ok"):
        raise Exception("can't resolve compare path '%s'" % compare_path)

    logging.info("Creating (if necessary) compare path: %s" % compare_path)
    mkdir_p(compare_path)
            
    if wait_status:
        status_path=os.path.join(primary_path, status_filename)
        logging.info("Using status file path: %s" % status_path)
    else: 
        status_path=None

    ### context for logging etc.
    ctx={
          "just_zppp": just_zppp
         ,"just_ppzp": just_ppzp
         ,"just_com":  just_com
         ,"just_list": just_zppp or just_ppzp or just_com
         
         ,"pp": primary_path
         ,"zp": compare_path
         ,"sp": status_path
         
         ,"pp_log" :{"up":    partial(ilog, primary_path)
                     ,"down":  partial(wlog, primary_path)
                     }
         ,"zp_log" :{"up":    partial(ilog, compare_path)
                     ,"down":  partial(wlog, compare_path)
                     }
         ,"topic_name": topic_name
         ,"exts": exts
         }

    ctx["tm"]=transition_manager(ctx)
    
    ppid=os.getppid()        
    logging.info("Process pid: %s" % os.getpid())
    logging.info("Parent  pid: %s" % ppid)
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
            maybe_process(ctx, code, msg, primary_path, compare_path, just_basename, dest_path)
        
        logging.debug("...sleeping for %s seconds" % polling_interval)
        sleep(polling_interval)

def filtre(exts):
    def _(path):
        _, ext=os.path.splitext(path)
        ext=ext.lstrip(".")
        return ext in exts
    return _
        


@pattern(dict, "ok", any, str, str, any)
def maybe_process_ok(ctx, _ok, _, primary_path, compare_path, just_basename, dest_path):
    
    if dest_path:
        logging.debug("Emptying dest path: %s" % dest_path)
        rmdir(dest_path)
        
        code, _msg=mkdir_p(dest_path)
        if code!="ok":
            raise Exception("Can't create path: %s" % dest_path)
        
    ### log rate limiter helper -- need to update status in context 'ctx'
    doOnTransition(ctx, "status_file.contents", "down", True, None)
    
    codep, primary_files=get_root_files(primary_path, strip_dirname=True)
    codec, compare_files=get_root_files(compare_path, strip_dirname=True)
    
    ### output some log info on transitions
    tm=ctx["tm"]
    tm.send(("pp_log", codep=="ok"))
    tm.send(("zp_log", codec=="ok"))
    
    ### not much to do if either path isn't accessible...
    if not codep.startswith("ok") or not codec.startswith("ok"):
        return
    
    exts=ctx["exts"]
    if exts is not None:
        primary_files=filter(filtre(exts), primary_files)
        compare_files=filter(filtre(exts), compare_files)
    
    def _mapper(path):
        bn=os.path.basename(path)
        return os.path.splitext(bn)[0]
    
    if just_basename:
        pfiles=map(_mapper, primary_files)
        cfiles=map(_mapper, compare_files)
    else:
        pfiles=primary_files
        cfiles=compare_files
    
    try:
        setpf=set(pfiles)
        setcf=set(cfiles)
        common=setpf.intersection(setcf)
        
        diff={
               "pp":     primary_path
              ,"zp":     compare_path
              ,"pp-zp":  list(setpf-setcf)
              ,"zp-pp":  list(setcf-setpf)
              ,"common": list(common)
              }
        
        topic_name=ctx["topic_name"]
        
        if topic_name is not None:
            diff["topic"]=topic_name
        
        if ctx["just_list"]:
            doout(ctx, diff, dest_path)
        else:
            stdoutj(diff)
            stdoutf()
            
    except Exception, e:
        logging.error("Can't compute diff between paths: %s" % str(e))

@pattern(dict, any, str, any, any, any)
def maybe_process_nok(ctx, _nok, _msg, _x, _y, _bn):
    """
    Rate limit logs
    """
    def wlog():
        logging.warning("Can't retrieve file contents from: %s" % ctx["sp"])
         
    doOnTransition(ctx, "status_file.contents", "down", False, wlog)


@patterned
def maybe_process(ctx, code, msg, primary_path, compare_path, just_basename): pass


def doout(ctx, listes, dest_path):

    if ctx["just_zppp"]:
        for e in listes["zp-pp"]:
            real_doout(dest_path, e)

    if ctx["just_ppzp"]:
        for e in listes["pp-zp"]:
            real_doout(dest_path, e)            
    
    if ctx["just_com"]:
        for e in listes["common"]:
            real_doout(dest_path, e)
            
            
def real_doout(dest_path, element):
    
    if dest_path is None:
        stdout(element)
        stdoutf()
    else:
        dfile=os.path.join(dest_path, element)
        code, msg=touch(dfile)
        if code!="ok":
            logging.warning("Can't touch file '%s'  (%s)" % (dfile, msg))
        

