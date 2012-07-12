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
    logging.info("Parent pid: %s" % ppid)
    logging.info("Starting loop...")
    
    min_marker=False
    hour_marker=False
    day_marker=False
    while True:
        if os.getppid()!=ppid:
            logging.warning("Parent terminated... exiting")
            break
        
        sec=d["sec"]+1
        min_marker=(sec==60)
        d["min_marker"]=min_marker
        d["sec"]=sec % 60
        
        if min_marker:
            _min=d["min"]+1
            hour_marker=(_min==60)
            d["hour_marker"]=hour_marker
            d["min"]=_min % 60
            
            if hour_marker:            
                hour=d["hour"]+1
                day_marker=(hour==24)
                d["hour"]=hour % 24
                
                if day_marker:                    
                    d["day"]=d["day"]+1
        
        if suppress_second_marker:
            if not min_marker and not hour_marker and not day_marker:
                sleep(ONE_SECOND)
                continue
               
        try:
            stdout(d)
            
            if separate_msg_marker:
                if min_marker:
                    stdout({"topic":"min_marker"})
                if hour_marker:
                    stdout({"topic":"hour_marker"})
                if day_marker:
                    stdout({"topic":"day_marker"})
        except:
            raise Exception("Exiting... probably broken pipe")
        
        sleep(ONE_SECOND)


