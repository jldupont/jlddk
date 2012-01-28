"""
    Created on 2012-01-28
    @author: jldupont
"""
import logging


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

if __name__=="__main__":
    import doctest
    doctest.testmod()
    