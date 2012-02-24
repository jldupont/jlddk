"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, sys, json, os
from time import sleep

from pyfnc import pattern, patterned

MTYPES=["task", "done", "error"]

def run(args,
        **_ 
        ):
    
    ctx=dict(args)
         
    ppid=os.getppid()    
    logging.info("Process pid: %s" % os.getpid())
    logging.info("Parent pid : %s" % ppid)
    logging.info("Starting loop...")
    while True:
        if os.getppid()!=ppid:
            logging.warning("Parent terminated... exiting")
            break

        try:
            iline=sys.stdin.readline()
            jso=json.loads(iline)
        except:
            try:    logging.debug("Can't JSON decode: %s" % iline)
            except: pass
            continue

        try:
            topic=jso["topic"]
        except:
            logging.warning("Can't find 'topic' member in json object: %s" % jso)
            continue
        
        code, msg=process(ctx, topic, jso)
        hcode(code, msg)

############################################################################################

@pattern("ok", str)
def hcode_ok(_, msg):
    pass



@pattern(any, any)
def hcode_any(code, msg):
    raise Exception("Unsupported code: %s" % code)

@patterned
def hcode(code, msg): pass



############################################################################################

def process(ctx, topic, jso):
    if topic==ctx["clock_topic"]:
        return hclock(ctx, jso)

    try:    
        prefix, mtype=topic.split("_")
        question=prefix.startswith("?")
        prefix=prefix.lstrip("?")
    except: return ("debug", "invalid topic name: %s" % topic)
    
    prefixes=ctx["prefixes"]
    if prefix not in prefixes:
        return ("debug", "nothing to do: %s" % topic)
    
    if mtype not in MTYPES:
        return ("debug", "mtype not interesting: %s" % mtype)
    
    return handle(ctx, question, prefix, mtype)

###########################################################################################    

def hclock(ctx, jso):
    ctx["_clock"]=jso
    return ("ok", None)

###########################################################################################






###########################################################################################
@pattern(dict, False, str, "error")
def handle_error(ctx, question, prefix, mtype):
    """
    """

@pattern(dict, False, str, "task")
def handle_task(ctx, question, prefix, mtype):
    """
    """

@pattern(dict, False, str, "done")
def handle_done(ctx, question, prefix, mtype):
    """
    """

@pattern(dict, any, any, any)
def handle_any(_ctx, question, prefix, mtype):
    """
    """
    q="?" if question else ""
    return ("debug", "nothing to do with: %s%s_%s" % (q, prefix, mtype))



@patterned
def handle(ctx, question, prefix, mtype):
    pass
