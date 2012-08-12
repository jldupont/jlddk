"""
    Created on 2012-01-19
    @author: jldupont
"""
import logging, yaml

from jlddk.tools_sys import prepare_mod, raise_if_not_ok
from jlddk.tools_os import resolve_path, file_contents

from agents.exc import *

def run( path_config=None
         #,args=[]
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
    
    entries=[]
    for agent_name in agents:
        logging.info("Preparing agent '%s'" % agent_name)
        module_name=agents[agent_name]
        mod=prepare_mod(module_name)
        try:
            vtable=getattr(mod, "__vtable__")
        except:
            raise Exception("Can't find '__vtable__' in agent's module")
        entries.append((agent_name, module_name, vtable, mod))
        
            
        
    logging.info("Loaded %s agents" % len(agents))
    
    mqueue=[{"topic": "init", "ctx": cdata},]
    while True:
        try:     
            msg=mqueue.pop(0)
        except:
            raise Exception("No more messages in queue")
        
        try:    topic=msg["topic"]
        except: 
            raise Exception("Message is missing 'topic' field...")
        
        ### broadcast the msg to all agents
        for agent_name, module_name, vtable, _module in entries:
            fnc=vtable.get(topic, None)
            if fnc is None:
                fnc=vtable.get("*", None)
                if fnc is None:
                    continue
            try:
                fnc(mqueue, msg)
            except ExcInfo, e:
                logging.info("(%s:%s) %s" % (agent_name, topic, e))
            except ExcWarn, e:
                logging.warning("(%s:%s) %s" % (agent_name, topic, e))
            except ExcErr,e:
                logging.error("(%s:%s) %s" % (agent_name, topic, e))
            except ExcCrit,e:
                raise               
            except ExcQuit:
                raise KeyboardInterrupt()
            except IOError:
                raise
            except Exception,e:
                logging.error("(%s:%s) %s" % (agent_name, topic, e))
            
        
        
    