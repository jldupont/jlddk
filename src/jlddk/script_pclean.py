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

    def filtre(pentry):
        user_match=(username is None) or (username==pentry.username)
        name_match=(prefix is None) or pentry.name.startswith(prefix)
        ppid_match=(ppid is None) or (pentry.ppid==ppid)
        return name_match and ppid_match and user_match

    def filtre_prefix(pentry):
        name_match=(prefix is None) or pentry.name.startswith(prefix)
        return name_match


    logging.info("Starting loop...")
    while True:
        
        plist=psutil.get_process_list()
        nlist=filter(filtre_prefix, plist)
        
        for p in nlist:
            logging.info("Name '%s' of pid '%s' of username '%s'" % (p.name, p.pid, p.username))

        flist=filter(filtre, plist)
        
        for p in flist:
            name=p.name
            pid=p.pid
            user=p.username
            
            details="'%s' with pid '%s' of user '%s'" % (name, pid, user)
            
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


