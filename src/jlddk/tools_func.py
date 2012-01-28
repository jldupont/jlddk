"""
    Created on 2012-01-27
    @author: jldupont
"""

def coroutine(func):
    def start(*args, **kwargs):
        cr=func(*args, **kwargs)
        cr.next()
        return cr
    start.__name__=func.__name__
    return start
