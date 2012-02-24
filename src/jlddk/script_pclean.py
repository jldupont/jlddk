"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, os, signal
from time import sleep
import psutil


def run(prefix=None, polling_interval=None
        ,force_kill=None
        ,username=None
        ,ppid=None
        ):


    def prefix_match(entry):
        if prefix is None:
            return True
        
        bns=map(os.path.basename, entry.cmdline)
        flist=filter(lambda x:x.startswith(prefix), bns)
        return len(flist)>0
    

    def filtre(pentry):
        user_match=(username is None) or (username==pentry.username)
        name_match=(prefix is None)   or (pentry.name.startswith(prefix))
        ppid_match=(ppid is None)     or (pentry.ppid==ppid)
        pmatch=prefix_match(pentry)
        
        return ppid_match and (name_match or pmatch) and user_match



    logging.info("Starting loop...")
    while True:
        
        plist=psutil.get_process_list()
        flist=filter(filtre, plist)
        
        for p in flist:
            cmdline=p.cmdline
            pid=p.pid
            user=p.username
            
            details="pid '%s' '%s' : %s" % (pid, user, cmdline)
            
            if not force_kill:
                logging.info("Would kill %s" % details)
            else:
                try:
                    os.kill(p.pid, signal.SIGTERM)
                    logging.info("Killed %s" % details)
                except:
                    try:
                        os.kill(p.pid, signal.SIGKILL)
                        logging.info("Killed %s" % details)
                    except:
                        logging.warning("Couldn't kill %s" % details)
        
        sleep(polling_interval)


