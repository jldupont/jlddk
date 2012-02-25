"""

    Ready --> Pending
    Ready --> Error
    Ready --> Stopped
    
    Pending --> Ready
    Pending --> Error
    Pending --> Stopped
    
    Error   --> Ready
    Error   --> Stopped


    Q:What if a task takes too much time to complete?
                    doesn't send a "done" or "error" message?
                    
    A: don't have any control over here.

    Input Messages:
    
        x_done
        x_error
        x_worker
        
    Output Messages:
    
        x_timeout
        ?x_task


    Created on 2012-01-27
    @author: jldupont
"""
import logging, sys, json, os
import types

from tools_sys import BrokenPipe
from tools_logging import setloglevel
from tools_func import transition_manager

from pyfnc import pattern, patterned, dic

MTYPES=["task", "done", "error", "worker"]

def run(args
        ,logconfig=None
        ,loglevel=None
        ,**_ 
        ):
    
    if logconfig is not None:
        logging.config.fileConfig(logconfig)

    setloglevel(loglevel)
    
    def dp(msg):
        def _(state):
            logging.debug(msg % state)
        return _
        
    
    tmctx={ 
            "worker": { "ch": dp("Worker is: %s"), "up": dp("Worker is: %s") }
           #,"state":  { "up": dp, "down": dp }
           }
    
    ctx=dict(args)
    ctx["_tm"]=transition_manager(tmctx)
         
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
        except KeyboardInterrupt:
            raise
        except:
            raise BrokenPipe("Broken Pipe...")

        #logging.debug("Received: %s" % iline)

        try:
            jso=json.loads(iline)
        except:
            try:    logging.debug("Can't JSON decode: %s" % iline)
            except: pass
            continue            
        
        #logging.debug("Received: %s" % jso)

        try:
            topic=jso["topic"]
        except:
            logging.warning("Can't find 'topic' member in json object: %s" % jso)
            continue
        
        code, msg=process(ctx, topic, jso)
        hcode(code, msg)

############################################################################################

@pattern("ok", any)
def hcode_ok(_, msg):
    pass

@pattern("debug", any)
def hcode_debug(_, msg):
    logging.debug(msg)

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
        task_type, mtype=topic.split("_")
        question=task_type.startswith("?")
        task_type=task_type.lstrip("?")
    except: 
        return ("debug", "invalid topic name: %s" % topic)
    
    logging.debug("Process: %s %s %s" % (question, task_type, mtype))
    
    task_types=ctx["task_types"]
    if task_type not in task_types:
        return ("debug", "nothing to do: %s (%s)" % (topic, task_type))
    
    if mtype not in MTYPES:
        return ("debug", "mtype not interesting: %s" % mtype)
    
    return handle(ctx, question, task_type, mtype)

###########################################################################################    

def hclock(ctx, _jso):
    """
    Have some timeouts expired?
    
    _$ttype: { "timeout": $timeout_left_in_seconds }
    """
    #ctx["_clock"]=jso
    tm=ctx["_tm"]
    
    timeout_state_report=ctx["timeout_state_report"]
    
    ### go through all 'ttype' and decrease their timeout
    ttypes=ctx["task_types"]
    for ttype in ttypes:
        
        ### state timeout
        timeout=tget(ctx, ttype, "timeout", 1)
        timeout=(timeout-1) if timeout>0 else 0
        tset(ctx, ttype, "timeout", timeout)
        
        ### state reporting
        ###
        timeout_report=tget(ctx, ttype, "report_state", timeout_state_report)
        
        if timeout_state_report!=0:
            if timeout_report==0:
                current=tget(ctx, ttype, "state", "ready")
                send_msg(False, ttype, "state", current)
        
        timeout_report=(timeout_report-1) if timeout_report>0 else timeout_state_report
        tset(ctx, ttype, "report_state", timeout_report)
        
        
        ### worker keep-alive timeout
        max_timeout_worker=ctx["max_timeout_worker"]
        wtimeout=tget(ctx, ttype, "timeout_worker", max_timeout_worker)
        wtimeout=(wtimeout-1) if wtimeout>0 else 0
        tset(ctx, ttype, "timeout_worker", wtimeout)
        
        if wtimeout==0:
            tm.send(("worker", "stopped"))
            tset(ctx, ttype, "state", "stopped")

    ### now, compute the "next" state
    for ttype in ttypes:
        
        current=tget(ctx, ttype, "state", "ready")
        new=compute(ctx, current, ttype)
        tset(ctx, ttype, "state", new)
        
        #tm.send(("state", new))
    
    return ("ok", None)


###########################################################################################
###
###  STATE-MACHINE
###

@pattern(dict, "ready", str)
def compute_1(ctx, _, ttype):
    """
    Timeout expired? we are ready to ask for a new task to be performed
    """
    timeout=tget(ctx, ttype, "timeout", 0)
    if timeout==0:
        
        ###  ?x_task
        ###
        send_msg(True, ttype, "task", {})
        max_pending=ctx["max_pending"]
        tset(ctx, ttype, "timeout", max_pending)
        return "pending"
    
    return "ready"


@pattern(dict, "error", str)
def compute_2(ctx, _, ttype):
    """
    timeout expired?  we can get out of "error" state
    """
    timeout=tget(ctx, ttype, "timeout", 0)
    if timeout==0:
        return "ready"
    return "error"

@pattern(dict, "pending", str)
def compute_3(ctx, _, ttype):
    """
    timeout expired? need to advise that there is potentially a problem with the worker...
    """
    timeout=tget(ctx, ttype, "timeout", 0)
    if timeout==0:
        
        ###  x_timeout
        ###
        send_msg(False, ttype, "timeout", {})
        return "ready"
    
    return "pending"


@pattern(dict, "stopped", str)
def compute_4(ctx, _, ttype):
    """
    worker now available? exit "stopped" state
    """
    timeout_worker=tget(ctx, ttype, "timeout_worker", 0)
    if timeout_worker > 0:
        tset(ctx, ttype, "timeout", 0)
        return "ready"
    
    return "stopped"
    

@pattern(any, any, any)
def compute_any(ctx, current, ttype):
    raise Exception("Unknown state: %s" % current)


@patterned
def compute(ctx, current, ttype): pass


###########################################################################################
###
### SUPPORT FUNCTIONS

def tgetall(ctx, ttype, default={}):
    return ctx.get("_"+ttype, default)

def tget(ctx, ttype, key, default=None):
    _ttype=ctx.get("_"+ttype, {})
    return _ttype.get(key, default)

def tset(ctx, ttype, key, value):
    _ttype=ctx.get("_"+ttype, {})
    _ttype[key]=value
    ctx["_"+ttype]=_ttype


def send_msg(question, ttype, mtype, msg_dic):
    try:
        q="?" if question else ""
        topic=q+ttype+"_"+mtype
        
        m=dic({"topic": topic}).update(msg_dic)
        
        sys.stdout.write(json.dumps(m)+"\n")
    except:
        pass


###########################################################################################
###
### MESSAGE HANDLING
###

@pattern(dict, False, types.UnicodeType, "worker")
def handle_worker(ctx, _question, ttype, _):
    """
    Keep alive message related to a specific task-type
    
    Reset timeout associated with task-type
    When this counter reaches 0 ===>  worker is considered off-line
    """
    max_timeout_worker=ctx["max_timeout_worker"]
    tset(ctx, ttype, "timeout_worker", max_timeout_worker)
    logging.debug("Worker keep-alive: %s" % ttype)
    
    tm=ctx["_tm"]
    tm.send(("worker", "started"))
    return ("ok", None)
    

@pattern(dict, False, types.UnicodeType, "error")
def handle_error(ctx, _question, ttype, _):
    """
    Specific "task type" in error ==> handle timeout
    
    Double the current timeout (min of 1 second) until max_timeout_error is reached
    """
    max_timeout=ctx["max_timeout_error"]
    timeout=tget(ctx, ttype, "timeout", 1)
    
    timeout=min(2, timeout)
    timeout=min(timeout*2, max_timeout)
    
    tset(ctx, ttype, "timeout", timeout)
    tset(ctx, ttype, "state",   "error")
    
    return ("ok", None)

@pattern(dict, False, types.UnicodeType, "task")
def handle_task(ctx, _question, ttype, _):
    """
    Cool... there is a dispatcher but we don't know if the task is going to get done...
    """
    return ("ok", None)

@pattern(dict, False, types.UnicodeType, "done")
def handle_done(ctx, _question, ttype, _):
    """
    If we receive this sort of message, 
    it probably means there is no more error related to this task-type
    
    Clear outstanding task
    """
    tset(ctx, ttype, "state", "ready")
    
    ### need to wait a bit between tasks...
    wait=ctx["wait"]
    tset(ctx, ttype, "timeout", wait)
    return ("ok", None)

@pattern(any, any, any, any)
def handle_any(_ctx, question, ttype, mtype):
    """ probably an error to end up here """
    q="?" if question else ""
    logging.debug(type(_ctx))
    logging.debug(type(question))
    logging.debug(type(ttype))
    logging.debug(type(mtype))
    return ("debug", "nothing to do with: %s%s_%s" % (q, ttype, mtype))


@patterned
def handle(ctx, question, task_type, mtype): pass


########################################################################3

