"""
    Created on 2012-01-19
    @author: jldupont
"""
import logging, os, time, yaml

from jlddk.tools_sys import prepare_callable_from_string, raise_if_not_ok
from jlddk.tools_os import resolve_path, file_contents

def run( path_config=None
         ,args=[]
        ,**_kw
        ):
    
    code, maybe_cpath=resolve_path(path_config)
    raise_if_not_ok(code, "Can't resolve configuration file path")
    
    code, maybe_contents=file_contents(maybe_cpath)
    raise_if_not_ok(code, "Can't resolve load configuration file")
    
    logging.info("Loading configuration file...")
    try:
        cdata=yaml.load(maybe_contents)
    except Exception,e:
        raise Exception("Problem with YAML config file: %s" % e)
    
    logging.info("Validating configuration file...")
    agents=cdata.get("agents", None)
    if agents is None:
        raise Exception("No 'agents' list found...")
    
    callables=[]
    for agent in agents:
        logging.info("Preparing agent '%s'" % agent)
        callables.append(prepare_callable_from_string(agents[agent]))
        
    logging.info("Loaded %s agents" % len(agents))
    
    