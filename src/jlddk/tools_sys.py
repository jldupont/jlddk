"""
    Created on 2012-01-27
    @author: jldupont
"""
import json, sys, re
import types
import logging
import importlib

def _echo(*pargs, **kargs):
    print pargs, kargs

def prepare_callable(module_name, function_name):
    try:
        mod=importlib.import_module(module_name)
    except:
        raise Exception("Can't import module '%s'" % module_name)
        
    try:
        fnc=getattr(mod, function_name)
    except:
        raise Exception("Module '%s' doesn't have a 'run' function" % mod)
    
    if not callable(fnc):
        raise Exception("Can't call 'run' function of callable '%S'" % module_name)
    
    return (mod, fnc)


def call(module_name, function_name, *pargs, **kargs):
    """
    >>> call("tools_sys", "_echo", "hello", key="value")
    ('hello',) {'key': 'value'}
    """
    try:
        mod=importlib.import_module(module_name)
    except:
        raise Exception("Can't import module '%s'" % module_name)
        
    try:
        fnc=getattr(mod, function_name)
    except:
        raise Exception("Module '%s' doesn't have a 'run' function" % mod)
    
    if not callable(fnc):
        raise Exception("Can't call 'run' function of callable '%S'" % module_name)
    
    return fnc(*pargs, **kargs)
    
    
def dnorm(d):
    """
    Normalize dictionary
    
    >>> dnorm({"SoMeKeY":"  spaces  "})
    {'somekey': 'spaces'}
    """
    r={}
    for e in d:
        try:    r[e.lower()]=d[e].strip()
        except: r[e.lower()]=d[e]
    return r


def dstrip(d):
    """
    Strip each element in a dict
    
    >>> dstrip({"e1":" v1", "e2":" v2 "})
    {'e1': 'v1', 'e2': 'v2'}
    """
    for e in d:
        try:    d[e]=d[e].strip()
        except: pass
    return d


def info_dump(d, align):
    fmt="%-"+str(align)+"s : %s"

    if type(d)==types.DictionaryType:        
        for key in d:
            logging.info(fmt % (key, d[key]))
            
    if type(d)==types.ListType:
        for el in d:
            key, value=el
            logging.info(fmt % (key, value))

def stdoutjs(jso):
    try:
        o=json.dumps(jso)
        sys.stdout.write(o+"\n")
    except:
        pass

def stdout(s):
    sys.stdout.write(s+"\n")

def stdout_flush():
    sys.stdout.flush()

def json_string(o):
    try:
        return json.dumps(o)
    except:
        return ""

def versa_filter(regexes, inp, filterin=True):
    """
    >>> liste=["in.zip", "out.txt", "out2.txt", "in2.zip"]
    >>> regexes=[r'^([a-zA-Z0-9\-_]+)\.zip$',]
    >>> print versa_filter(regexes, liste)
    ['in.zip', 'in2.zip']
    >>> print versa_filter(regexes, liste, filterin=False)
    ['out.txt', 'out2.txt']
    >>> print versa_filter(regexes, "input.zip")
    input.zip
    """
    if regexes is None:
        return inp
    
    just_one_element=False
    if type(inp)!=types.ListType:
        inp=[inp]
        just_one_element=True
    
    rgs=[]
    for regex in regexes:
        rgs.append(re.compile(regex))
    
    result=[]
    for regex in rgs:
        r=filter(filterfunc(regex, filterin), inp)
        result.extend(r)
    
    if just_one_element:
        return result[0]
    
    return result

def filterfunc(regex, filterin=True):
    """
    >>> import re
    >>> regex=re.compile(r'^([a-zA-Z0-9\-_]+)\.zip$')
    >>> liste=["in.zip", "out.txt", "in2.zip", "out2.txt"]
    >>> result=filter(filterfunc(regex), liste)
    >>> print result
    ['in.zip', 'in2.zip']
    >>> result2=filter(filterfunc(regex, filterin=False), liste)
    >>> print result2
    ['out.txt', 'out2.txt']
    """
    def fn(el):
        try:
            groups=regex.match(el).groups()
            return len(groups[0]) > 0 and filterin
        except:
            return not filterin
        
    return fn


if __name__=="__main__":
    import doctest
    doctest.testmod()
    