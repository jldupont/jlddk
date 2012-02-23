"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, sys, json
from time import sleep

ONE_SECOND=1

def stdout(jo):
    try:    sys.stdout.write(json.dumps(jo)+"\n")
    except: pass

def run(topic_name=None):

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

    logging.info("Starting loop...")
    while True:
        
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
        
        stdout(d)
        
        sleep(ONE_SECOND)

