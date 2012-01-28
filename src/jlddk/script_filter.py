"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, re, sys, json, types
from time import sleep
from tools_func import coroutine
from tools_sys import json_string, stdout, info_dump, prepare_callable
from tools_sys import versa_filter
from tools_logging import setloglevel


def run(inr=None, outr=None, member=None, module=None, loglevel="info", logconfig=None):
    
    if logconfig is not None:
        logging.config.fileConfig(logconfig)

    setloglevel(loglevel)
    
    if module is not None:
        if inr or outr:
            raise Exception("Regexes can't be used with Python module 'run'")
    
    regexin=[]
    regexout=[]
    if inr or outr:
        logging.info("Compiling regexes...")
    
        for rg in inr:
            try:
                crg=re.compile(rg)
                regexin.append(crg)
            except:
                raise Exception("Compiling 'in' regex: %s" % rg)
            
        for rg in outr:
            try:
                crg=re.compile(rg)
                regexout.append(crg)
            except:
                raise Exception("Compiling 'out' regex: %s" % rg)
            
    if module is not None:
        logging.info("Preparing callable 'run' from module: %s" % module)
        fnc=prepare_callable(module, "run")
    else: fnc=None
            
    ## CONTEXT for the pipeline #####################################
    ctx={"in": regexin, "out": regexout, "fnc": fnc, "member": member}
    
    p1=procl1(ctx)
    
    logging.info("Starting loop...")
    while True:
        
        line=sys.stdin.readline()
        try:
            jso=json.loads(line)
        except:
            logging.error("JSON decode: %s" % line)
            continue
        
        logging.debug("...extracting member from JSON object")
        try:
            mo=jso[member]
        except:
            logging.error("Can't find member '%s'" % member)
            continue
        
        p1.send((jso, mo))


@coroutine
def procl1(ctx):
    """ handling 'in' regexes' """
    
    p2=procl2(ctx)
    
    while True:
        jso, mo=(yield)
        
        try:
            r=versa_filter(ctx["in"], mo, filterin=True)
        except:
            logging.error("Can't apply 'in' regexes to: %s" % mo)
            return
        
        p2.send((json, r))
        
        
@coroutine
def procl2(ctx):
    """ handling 'out' regexes' """
    while True:
        jso, mo=(yield)
        print mo
    