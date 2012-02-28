"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, sys, json, os, select, time
from tools_os import resolve_path, getsubdirs
from tools_func import simple_transition_manager, transition_manager 

from pyfnc import partial

def stdout(jo):
    try:    
        sys.stdout.write(json.dumps(jo)+"\n")
        sys.stdout.flush()
    except:
        raise Exception("Exiting... probably broken pipe")

def run( path=None
        ,polling_interval=None
        ,topic=None
        ,always=None
        ,**_
        ):

    code, path=resolve_path(path)
    if not code.startswith("ok"):
        raise Exception("Can't resolve path...: %s" % path)

    def loginfo(path, state, *_):
        logging.info("Path state '%s': %s" % (path, state))

    ctx={"topic": topic, "path": path, "always":always}
    ctx["_path"]={
                  "previous": "ok"
                  ,"ch": partial(loginfo, path)
                  }
    tm=transition_manager(ctx)
    

    ppid=os.getppid()
    logging.info("Process pid: %s" % os.getpid())
    logging.info("Parent pid : %s" % ppid)
    logging.info("Starting loop...")    
    while True:
        if os.getppid()!=ppid:
            logging.warning("Parent terminated... exiting")
            break

        code, maybe_subdirs=getsubdirs(path)
        tm.send(("_path", code))
        if code.startswith("ok"):
            process(ctx, maybe_subdirs)
        
        start_time=time.time()
        while True:
            ir, _w, _e=select.select([sys.stdin], [], [], polling_interval)
            if len(ir):
                iline=sys.stdin.readline()
                sys.stdout.write(iline)
                
            elapsed_time = time.time() - start_time
            if elapsed_time > polling_interval:
                break


def getmtime(path):
    return (path, os.path.getmtime(path))

def getchanges(ctx, entry):
    path, mtime=entry
    result=simple_transition_manager(ctx, path, mtime)
    return (path, mtime, result)

def process(ctx, subdirs):
    topic=ctx["topic"]
    path=ctx["path"]
    always=ctx["always"]
    
    minfo=map(getmtime, subdirs)
    
    entries=map(partial(getchanges, ctx), minfo)
    
    for entry in entries:
        path, mtime, result=entry
        maybe_tr, _=result
        if maybe_tr=="tr" or always:
            output(topic, path, mtime)


def output(topic, path, mtime):
    
    d={
       "topic": topic
       ,"path": path
       ,"mtime": mtime
       }
    stdout(d)

#
#