"""
    Created on 2012-02-08
    @author: jldupont
"""
import json
from tools_os import file_contents

from pyfnc import patterned, pattern

def debug(*p):
    print p
    return p[0]

def batch(l, size):
    """
    >>> for b in batch([1,2,3,4,5,6], 2): print b
    [1, 2]
    [3, 4]
    [5, 6]
    >>> for b in batch([1], 2): print b
    [1]
    >>> for b in batch([], 2): print b
    """
    index=0
    while True:
        sub=l[index:index+size]
        index=index+size
        if len(sub)==0:
            break
        
        yield sub
        


def check_if_ok(filepath, default="ok"):
    """
    Check for 'ok' string or JSON object with 'ok' code
    
    >>> check_if_ok(None)
    ('ok', None)
    >>> check_if_ok("/tmp/non_existing_path")
    ('error', 'empty file')
    >>> from tools_os import quick_write, rm
    >>> p="/tmp/_jlddk_tools_misc_test"
    >>> quick_write(p, "ok")
    ('ok', '/tmp/_jlddk_tools_misc_test')
    >>> check_if_ok(p)
    ('ok', None)
    >>> quick_write(p, '''{"code": "ok"}''')
    ('ok', '/tmp/_jlddk_tools_misc_test')
    >>> check_if_ok(p)
    ('ok', None)
    >>> quick_write(p, '''{"code": "error"}''')
    ('ok', '/tmp/_jlddk_tools_misc_test')
    >>> check_if_ok(p) # doctest: +ELLIPSIS
    ('error', ...
    >>> rm(p)
    ('ok', '/tmp/_jlddk_tools_misc_test')
    """
    
    if filepath is None:
        return (default, None)
    
    code, maybe_contents=file_contents(filepath)
    return checkok(code, maybe_contents)


@pattern(str, None)
def checkok_empty(_, contents):
    return ("error", "empty file")

@pattern("ok", str)
def checkok_ok(_, contents):
    contents=contents.strip()
    
    if contents.startswith("ok"):
        return ("ok", None)
    
    try:
        jo=json.loads(contents)
        if jo["code"]=="ok":
            return ("ok", None)
    except:
        return ("error", "invalid format")
    
    return ("error", "'ok' code not found")

@pattern(any, any)
def check_nok(code, msg):
    return (code, msg)

@patterned
def checkok(code, maybe_contents): pass


if __name__=="__main__":
    import doctest
    doctest.testmod()
