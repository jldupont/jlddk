"""
    Created on 2012-02-17
    @author: jldupont
    
"""
import logging, sys
import time, select

from tools_sys import BrokenPipe

def run(ostr=None,
        polling_interval=None
        ,**_
        ):
        
    logging.info("Starting... ")
    while True:
        
        try:
            sys.stdout.write(ostr+"\n")
        except:
            raise BrokenPipe("broken pipe...")

        logging.debug("...waiting for %s seconds (max)" % polling_interval)
        
        ### Implement a "pass-through" for stdin --> stdout
        ###  whilst also handling a maximum time-out
        start_time=time.time()
        while True:
            ir, _w, _e=select.select([sys.stdin], [], [], polling_interval)
            if len(ir):
                iline=sys.stdin.readline()
                sys.stdout.write(iline)
                
            elapsed_time = time.time() - start_time
            if elapsed_time > polling_interval:
                break
