"""
    Created on 2012-01-27
    @author: jldupont
"""
import pyinotify
import logging, sys, json
from tools_logging import setloglevel
from tools_misc import retry


def run(path_source=None, loglevel="info", logconfig=None):
    
    if logconfig is not None:
        logging.config.fileConfig(logconfig)

    setloglevel(loglevel)

    wm = pyinotify.WatchManager()
    
    def set_watch():
        wm.add_watch(path_source, pyinotify.ALL_EVENTS, rec=True, auto_add=True, quiet=False)
        return wm
    
    retry(set_watch, logmsg="Source path '%s' isn't available yet... retrying" % path_source)
    logging.info("Source path '%s' available" % path_source)

    eh = EventHandler()

    # notifier
    notifier = pyinotify.Notifier(wm, eh)
    notifier.loop()


class EventHandler(pyinotify.ProcessEvent):
    
    def _dispatch(self, event):
        
        d={"event_name":  event.maskname
           ,"path_source": event.path
           ,"path_name": event.pathname
           ,"path_base": event.name
           ,"path_mask": event.mask
           }
        
        try:
            sys.stdout.write(json.dumps(d)+"\n")
        except:
            pass

        sys.stdout.flush()
        
    def __getattr__(self, name):
        if name.startswith("process_IN"):
            return self._dispatch
    

