"""
    Created on 2012-01-28
    @author: jldupont
"""
import logging, hashlib


def setloglevel(level_name):
    """
    >>> import logging
    >>> setloglevel("info")
    >>> logging.debug("test")
    
    """
    try:
        ll=getattr(logging, level_name.upper())
        logger=logging.getLogger()
        logger.setLevel(ll)
    except:
        raise Exception("Invalid log level name: %s" % level_name)

class FilterDuplicates(logging.Filter):
    """
    Everything before the ':' marker is considered to be the "signature" for a log event
    
    - All DEBUG level log go through
    - All "progress" report go through
    - All messages with a ":" separator (for contextual info) are passed
    - Other messages are filtered for duplicates 
    """
    occured=[]
    
    def filter(self, record):
        if record.levelname=="DEBUG":
            return 1
        msg=record.getMessage()
        if msg.startswith("progress") or msg.startswith("Progress"):
            return 1
        
        try:
            bits=msg.split(":")
            if len(bits)>1:
                return 1
            
            signature_hash=hashlib.md5(msg).hexdigest()
            if signature_hash in self.occured:
                return 0
            
            self.occured.append(signature_hash)
            record.msg="*"+msg
        except Exception,e:
            print e
            ### let it pass...
            pass
        
        return 1
        


def enable_duplicates_filter():
    logger=logging.getLogger()
    logger.addFilter(FilterDuplicates())


if __name__=="__main__":
    import doctest
    doctest.testmod()
    