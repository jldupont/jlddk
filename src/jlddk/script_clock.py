"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, sys, json, os
from time import sleep

ONE_SECOND=1

def stdout(jo):
    sys.stdout.write(json.dumps(jo)+"\n")
        

def run(topic_name=None
        ,separate_msg_marker=False
        ,suppress_second_marker=False
        ,seconds_count=None
        ,tick_at_start=False
        ,**_
        ):

    ### elapsed
    d={"topic": topic_name
       ,"sec": 0
       ,"min": 0
       ,"hour": 0
       ,"day": 0
       ,"min_marker": False
       ,"hour_marker": False
       ,"day_marker": False
    }
    

    ppid=os.getppid()        
    logging.info("Process pid: %s" % os.getpid())
    logging.info("Parent pid:  %s" % ppid)
    logging.info("Starting loop...")
    
    if tick_at_start:
        send_tick()
        
    
    while True:
        if os.getppid()!=ppid:
            logging.warning("Parent terminated... exiting")
            break

        if seconds_count is None:
            d=mode_default(d, suppress_second_marker, separate_msg_marker)
        else:
            mode_interval(seconds_count)
            
def mode_interval(interval_in_seconds):
    
    sleep(interval_in_seconds)
    send_tick()
        

def send_tick():
    stdout({"topic":"tick"})


def mode_default(d, suppress_second_marker, separate_msg_marker):

    d["min_marker"]=False
    d["hour_marker"]=False
    d["day_marker"]=False
    
    sec=d["sec"]+1
    d["min_marker"]=(sec==60)
    d["sec"]=sec % 60
    
    if d["min_marker"]:
        _min=d["min"]+1
        d["hour_marker"]=(_min==60)
        d["min"]=_min % 60
        
        if d["hour_marker"]:            
            hour=d["hour"]+1
            d["day_marker"]=(hour==24)
            d["hour"]=hour % 24
            
            if d["day_marker"]:                    
                d["day"]=d["day"]+1
    
    #logging.debug(" sec(%s) min_marker(%s) hour_marker(%s) day_marker(%s)" % (sec, min_marker, hour_marker, day_marker))
    if suppress_second_marker:
        if not d["min_marker"] and not d["hour_marker"] and not d["day_marker"]:
            sleep(ONE_SECOND)
            return d
           
    try:
        stdout(d)
        
        if separate_msg_marker:
            if d["min_marker"]:
                stdout({"topic":"min_marker"})
            if d["hour_marker"]:
                stdout({"topic":"hour_marker"})
            if d["day_marker"]:
                stdout({"topic":"day_marker"})
    except:
        raise Exception("Exiting... probably broken pipe")
    
    sleep(ONE_SECOND)

    return d

