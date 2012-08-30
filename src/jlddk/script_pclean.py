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
        ,**_
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


    liste=[]
    this_pid=os.getpid()
    this_ppid=os.getppid()
    logging.info("Process pid: %s" % this_pid)
    logging.info("Parent pid:  %s" % this_ppid)
    logging.info("Starting loop...")
    while True:
        if os.getppid()!=this_ppid:
            logging.warning("Parent terminated... exiting")
            break
        
        #deprecated in psutil
        #plist=psutil.get_process_list()
        #flist=filter(filtre, plist)
        
        for proc in psutil.process_iter():
            
            ## make sure we get a fresh copy
            p=psutil.Process(proc.pid)
            
            if filtre(p):                
                cmdline=p.cmdline

                ## skip ourself!                
                if p.pid != this_pid:
                    user=p.username
                    
                    details="pid '%s' '%s' : %s" % (p.pid, user, cmdline)
                    do_kill(p.pid, details, force_kill)
                    
        
        logging.debug("Sleeping...")
        sleep(polling_interval)


def do_kill(pid, details, force_kill):
    if not force_kill:
        logging.info("Would kill %s" % details)
    else:
        try:
            os.kill(pid, signal.SIGTERM)
            logging.info("Killed %s" % details)
        except:
            try:
                os.kill(pid, signal.SIGKILL)
                logging.info("Killed %s" % details)
            except:
                logging.warning("Couldn't kill %s" % details)
    
