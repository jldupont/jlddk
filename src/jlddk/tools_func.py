"""
    Created on 2012-01-27
    @author: jldupont
"""
import types
from pyfnc import patterned, pattern, coroutine


@pattern(dict, str, "up", bool, types.FunctionType)
def doOnTransition_up(ctx, param, _, current_state, func):
    
    previous_state=ctx.get(param, None)
    ctx[param]=current_state
    
    if (not previous_state or previous_state is None) and current_state:
        func()
    

@pattern(dict, str, "down", bool, types.FunctionType)
def doOnTransition_down(ctx, param, _, current_state, func):
    
    previous_state=ctx.get(param, None)
    ctx[param]=current_state
    
    if (previous_state or previous_state is None) and not current_state:
        func()

@pattern(dict, any, any, bool, None)
def doOnTransition_none(ctx, param, _, current_state, func):
    ctx[param]=current_state


@patterned
def doOnTransition(ctx, param, tr_type, current_state, func):
    """
    >>> import sys
    >>> fn=lambda: sys.stdout.write("test")
    >>> ctx={}
    >>> doOnTransition(ctx, "param", "up", False, fn)
    >>> doOnTransition(ctx, "param", "up", True, fn)
    test
    >>> doOnTransition(ctx, "param", "up", True, fn)
    >>> doOnTransition(ctx, "param", "up", True, fn)
    >>> doOnTransition(ctx, "param", "up", False, fn)
    >>> doOnTransition(ctx, "param", "up", True, fn)
    test
    """
    

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
