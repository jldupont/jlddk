"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, sys, os
from tools_sys import prepare_callable
from tools_logging import setloglevel


def run(module=None, function=None, function_args=None, loglevel="info", logconfig=None):
    
    if logconfig is not None:
        logging.config.fileConfig(logconfig)

    setloglevel(loglevel)

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
            iline=sys.stdin.readline()
        except:
            raise Exception("Exiting... probably broken pipe")

        try:
            oline=fnc(iline, *function_args)
        except KeyboardInterrupt:
            raise
        except Exception, e:
            try:    logging.error("Error processing '%s' : %s" % (iline[:20], str(e)))
            except: pass
            
        if oline is not None:
            try:
                sys.stdout.write(oline)
            except:
                try:
                    sys.stdout.write(str(oline)+"\n")
                except:
                    raise Exception("Exiting... probably broken pipe")

