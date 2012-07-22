"""
    Created on 2012-01-27
    @author: jldupont
"""
import json, sys, re, os
import types
import logging
import importlib

from jlddk.tools_logging import setloglevel, enable_duplicates_filter, setup_syslog

class BrokenPipe(Exception): pass


def process_command_line(parser):
    parser.add_argument('-lc',  dest="logconfig", type=str,  help="Logging configuration file", choices=["debug", "info", "warning", "error"])
    parser.add_argument('-ll',  dest='log_level',     type=str,            help="Log Level", default="info", choices=["debug", "info", "warning", "error"])
    parser.add_argument('-kdf', dest='log_keepdup',   action="store_true", help="Keep duplicate log entries", default=False)
    parser.add_argument('-lsl', dest='log_syslog',    action="store_true", help="Enable syslog", default=False)
    args=dnorm(vars(parser.parse_args()))
    
    if (not args["log_keepdup"]):
        enable_duplicates_filter()
        
    if (args["log_syslog"]):
        setup_syslog()
        
    setloglevel(args["log_level"])
    info_dump(args, 20)
    return args

def raise_if_not_ok(code, msg):
    if not code.startswith("ok"):
        raise Exception(msg)


def _echo(*pargs, **kargs):
    print pargs, kargs

def prepare_callable_from_string(st):
    """
    mod.fnc
    """
    mod, fnc=os.path.splitext(st)
    return prepare_callable(mod, fnc.strip("."))

def prepare_mod(module_name):
    try:
        mod=importlib.import_module(module_name)
    except:
        raise Exception("Can't import module '%s'" % module_name)
    return mod


def prepare_callable(module_name, function_name):
    try:
        mod=importlib.import_module(module_name)
    except:
        raise Exception("Can't import module '%s'" % module_name)
        
    try:
        fnc=getattr(mod, function_name)
    except:
        raise Exception("Module '%s' doesn't have a '%s' function" % (mod, function_name))
    
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
        raise BrokenPipe()

def stdout(s):
    try:
        sys.stdout.write(s+"\n")
    except:
        raise BrokenPipe()

def stdout_flush():
    try:
        sys.stdout.flush()
    except:
        raise BrokenPipe()

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
    