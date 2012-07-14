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
            
        if oline is not None:
            try:
                sys.stdout.write(oline)
            except:
                try:
                    sys.stdout.write(str(oline)+"\n")
                except:
                    raise Exception("Exiting... probably broken pipe")

