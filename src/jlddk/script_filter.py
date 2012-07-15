"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, sys, os
from tools_sys import prepare_callable


def run(module=None, function=None, function_args=None, 
        no_filter_empty=None
        ,**_):
    
    try:                
        logging.info("Preparing callable '%s' from module '%s'" % (function, module))
        _mod, fnc=prepare_callable(module, function)
    except:
        raise Exception("%s.%s isn't callable..." %(module, function))

    try:                
        init_function_name="%s_init" % function
        logging.info("Preparing init '%s' from module '%s'" % (init_function_name, module))
        _mod, fnc_init=prepare_callable(module, init_function_name)
    except Exception,e:
        logging.info("No or errored init function...: %s" % e)
        fnc_init=None

    if fnc_init is not None:
        try:
            logging.debug("Calling init function...")
            fnc_init(*function_args)
        except:
            raise Exception("Error calling init function")

    ppid=os.getppid()            
    logging.info("Process pid: %s" % os.getpid())
    logging.info("Parent pid : %s" % ppid)
    logging.info("Starting loop...")
    while True:
        if os.getppid()!=ppid:
            logging.warning("Parent terminated... exiting")
            break
        
        try:
            iline=sys.stdin.readline().strip(" \n")
        except:
            raise Exception("Exiting... probably broken pipe")

        if not no_filter_empty:
            if iline=="":
                logging.debug("Skipping empty line...")
                continue

        try:
            oline=fnc(iline, *function_args)
        except KeyboardInterrupt:
            raise
        except Exception, e:
            try:    logging.error("Error processing '%s' : %s" % (iline[:20], str(e)))
            except: pass
            continue

        if oline is None:
            logging.debug("No return value from called function")
            continue
        
        try:
            ostr=str(oline).strip("\n")
        except:
            logging.error("Error trying to stringify return string... continuing")
            continue
            
        try:
            sys.stdout.write(ostr+"\n")
        except:
            raise Exception("Exiting... probably broken pipe")

