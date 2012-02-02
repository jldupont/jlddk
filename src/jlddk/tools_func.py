"""
    Created on 2012-01-27
    @author: jldupont
"""
import functools

def coroutine(func):
    @functools.wraps(func)
    def start(*args, **kwargs):
        cr=func(*args, **kwargs)
        cr.next()
        return cr
    start.__name__=func.__name__
    return start


@coroutine
def check_transition():
    """
    Reports transitions
    
    >>> lt=check_transition()
    >>> print lt.send(False)
    ('tr', 'down')
    >>> print lt.send(False)
    ('nop', None)
    >>> print lt.send(True)
    ('tr', 'up')
    >>> print lt.send(True)
    ('nop', None)
    >>> print lt.send(False)
    ('tr', 'down')
    >>> print lt.send(False)
    ('nop', None)
    """
    last_status=None
    result=("nop", None)
    
    while True:
        status=(yield result)
        
        if status!=last_status:
            direction="up" if last_status==False else "down"
            last_status=status
            result=("tr", direction)
        else:
            result=("nop", None)


if __name__=="__main__":
    import doctest
    doctest.testmod()
