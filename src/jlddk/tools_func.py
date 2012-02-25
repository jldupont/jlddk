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
    
@pattern(None, None)
def is_trans_NN(previous, current):
    return ('nop', None)

@pattern(None, bool)
def is_trans_NB(previous, current):
    return ('tr', "up" if current is True else "down")
    
@pattern(False, False)
def is_trans_FF(previous, current):
    return ("nop", None)

@pattern(True, True)
def is_trans_TT(previous, current):
    return ("nop", None)
    
@pattern(True, False)
def is_trans_TF(previous, current):
    return ("tr", "down")

@pattern(False, True)
def is_trans_FT(previous, current):
    return ("tr", "up")
    
@pattern(None, str)
def is_trans_NS(previous, current):
    return ("tr", "up")
    
@pattern(str, str)
def is_trans_SS(previous, current):
    if previous!=current:
        return ("tr", "ch")
    return ("nop", None)
    
@patterned
def is_trans(previous, current):
    """
    >>> is_trans(True, True)
    ('nop', None)
    >>> is_trans(False, False)
    ('nop', None)
    >>> is_trans(True, False)
    ('tr', 'down')
    >>> is_trans(False, True)
    ('tr', 'up')
    >>> is_trans(None, None)
    ('nop', None)
    >>> is_trans(None, True)
    ('tr', 'up')
    >>> is_trans(None, False)
    ('tr', 'down')
    """

@coroutine
def transition_manager(ctx):
    """
    ctx[param]={ "state": state, "up": fnc, "down": fnc}
    
    >>> import logging
    >>> fu=lambda:logging.warning("up")
    >>> fd=lambda:logging.warning("down")
    >>> ctx={"test":{"up": fu, "down":fd}}
    >>> tm=transition_manager(ctx)
    >>> tm.send(("test", True))   ### warning output 'up'
    >>> tm.send(("test", True))
    >>> tm.send(("test", False))  ### warning output 'down'
    >>> tm.send(("test", False))
    """    
    while True:
        param, current_state=(yield)
        cparam=ctx.get(param, {})
        
        previous_state=cparam.get("previous", None)
        maybe_tr, maybe_dir=is_trans(previous_state, current_state)
        cparam["previous"]=current_state
        ctx[param]=cparam
        
        if maybe_tr=="tr":
            fnc=cparam.get(maybe_dir, None)
            if fnc is not None:
                try:
                    fnc(current_state)
                except:
                    fnc()
        
        

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
