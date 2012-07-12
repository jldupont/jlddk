"""
    Created on 2012-02-17
    @author: jldupont
    
"""
import logging, sys, os 

from tools_sys import BrokenPipe

def run(iformat=None
        ,separator=None
        ,**_
        ):
        
    if separator is None or separator=="":
        separator=" "
        
    num_params=iformat.count("%s")
    logging.info("Expected number of input params: %s" % num_params)
        
    ppid=os.getppid()        
    logging.info("Process pid: %s" % os.getpid())
    logging.info("Parent pid:  %s" % ppid)
    logging.info("Starting loop...")
    while True:
        if os.getppid()!=ppid:
            logging.warning("Parent terminated... exiting")
            break
            
        try:
            iline=sys.stdin.readline().strip()
            if len(iline)==0:
                continue
        except:
            raise Exception("Exiting... probably broken pipe")
        
        params=iline.split(separator)
        
        logging.debug("Params: %s" % params)
        try:
            result=iformat % tuple(params)
        except Exception,e:
            logging.error(e)
            continue
        
        try:
            sys.stdout.write(result+"\n")
        except:
            raise BrokenPipe("broken pipe...")

