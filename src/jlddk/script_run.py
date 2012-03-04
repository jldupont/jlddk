"""
    Created on 2012-01-19
    @author: jldupont
"""
import logging, os, time

from jlddk.tools_sys import prepare_callable, stdout, stdout_flush

def run(_args 
        ,module_name=None
        ,function_name=None
        ,fargs=None
        ,polling_interval=None
        ,**_kw
        ):
    
    logging.debug("Preparing callable...")
    
    try:
        _mod, fn=prepare_callable(module_name, function_name)
    except:
        raise Exception("Can't prepare callable: %s.%s" % (module_name, function_name))
    
    ppid=os.getppid()
    logging.info("Process pid: %s" % os.getpid())
    logging.info("Parent pid : %s" % ppid)
    logging.info("Starting loop...")
    while True:
        if os.getppid()!=ppid:
            logging.warning("Parent terminated... exiting")
            break

        try:
            result=fn(*fargs)
        except Exception, e:
            logging.warning("Problem with callable: %s" % str(e))
        
        if result is not None:
            stdout(result)
            stdout_flush()
            
        logging.debug("...sleeping for %s seconds" % polling_interval)
        time.sleep(polling_interval)
        
