"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, sys, json, os, select, time, types

from pyfnc import patterned, pattern

def stdout(jo):
    try:    
        sys.stdout.write(json.dumps(jo)+"\n")
        sys.stdout.flush()
    except:
        raise Exception("Exiting... probably broken pipe")


def run( ctx 
        ,polling_interval=None
        ,**_
        ):

    ctx["pairs"]={}
    ctx["count"]=0

    ppid=os.getppid()
    logging.info("Process pid: %s" % os.getpid())
    logging.info("Parent pid : %s" % ppid)
    logging.info("Starting loop...")    
    while True:
        if os.getppid()!=ppid:
            logging.warning("Parent terminated... exiting")
            break

        ### PASS-THROUGH LOGIC
        ######################
        start_time=time.time()
        while True:
            ir, _w, _e=select.select([sys.stdin], [], [], polling_interval)
            if len(ir):
                iline=sys.stdin.readline()
                oline=process_input(ctx, iline)
                if oline is not None:
                    sys.stdout.write(oline)
                    sys.stdout.flush()
                
            elapsed_time = time.time() - start_time
            if elapsed_time > polling_interval:
                break

        perform_update(ctx)
        ctx["count"]=ctx["count"]+1
        
        logging.debug("...end of cycle #%s" % ctx["count"])
        #### /while
        

def process_input(ctx, iline):
    """
    1- first check if we are dealing with a JSON object
    2- next, check if topic match
    3- and make sure the required fields are present
    --
    4- 
    
    """
    try:
        jso=json.loads(iline)
        topic=jso["topic"]
        assert(topic==ctx["itopic"])
        keyfieldname=ctx["key"]
        valuefieldname=ctx["value"]
        
        ### if we can't extract those, get out!
        key=jso[keyfieldname]
        value=jso[valuefieldname]
    except:
        ### pass-through
        logging.debug("pass-through: %s" % iline)
        return iline
    
    logging.debug("Got: {%s:%s}" % (key, value))
    
    ### at this point, we have everything we need
    ###  to perform our work
    pairs=ctx["pairs"]
    
    entry=pairs.get(key, (0, 0, 0, False))
    _last_update_count, _last_change_count, last_value, _stability=entry
    
    result=handle(ctx, entry, key, value, value==last_value)
    if result is None:
        result=""
        
    return iline+result

#######################################################################################    

@pattern(dict, types.TupleType, types.UnicodeType, any, True)
def handle_nochange(ctx, entry, key, _value, _):
    """
    No change --> just update "last_update_count"
    """
    _last_update_count, last_change_count, last_value, stability=entry
    current_count=ctx["count"]
    entry=(current_count, last_change_count, last_value, stability)
    pairs=ctx["pairs"]
    pairs[key]=entry
    return None
    

@pattern(dict, types.TupleType, types.UnicodeType, any, False)
def handle_change(ctx, entry, key, value, _):
    """
    There is a change...
    """
    _last_update_count, _last_change_count, _last_value, _stability=entry
    current_count=ctx["count"]
    entry=(current_count, current_count, value, False)
    pairs=ctx["pairs"]
    pairs[key]=entry
    return None
    
@patterned
def handle(ctx, entry, key, value, changed): pass


#######################################################################################

def perform_update(ctx):
    """
    check for 'stale' k:v pairs
    
    Use "modular arithmetic" will a sufficiently high circumference
     ensuring that runovers don't happen
    """
    hin=ctx["hin"]
    timeout=ctx["timeout"]
    current_count=ctx["count"]
    
    states=[]
    new={}
    pairs=ctx["pairs"]
    for key in pairs:
        entry=pairs[key]
        last_update_count, last_change_count, last_value, stability=entry

        ### check if stale...
        if (current_count - last_update_count) % 8192 > timeout:
            logging.info("Deleting stale key: %s" % key)
            continue
        
        ### check if stable...
        if (current_count - last_change_count) % 8192 >= hin:
            if not stability:
                logging.info("Stable {%s:%s}" % (key, last_value))
            
            ### take current count as "last_change_count"
            ###  trickery to keep complexity low...
            cc=(current_count - hin) % 8192
            new[key]=(last_update_count, cc, last_value, True)
            states.append((key, last_value, True))  ## stable
            continue
        else:
            states.append((key, last_value, False)) ## !stable
            new[key]=(last_update_count, last_change_count, last_value, False)
            
    ### clean dict without stale entries
    ctx["pairs"]=new
    
    use_kv=ctx["use_kv"]
    otopic=ctx["otopic"]
    for entry in states:
        key, value, stability=entry
        if use_kv:
            m={"topic":otopic, ctx["key"]: key, ctx["value"]: value, "stable": stability}
        else:
            m={"topic":otopic, "key": key, "value": value, "stable": stability}
        stdout(m)


#######################################################################################
#
#
#

