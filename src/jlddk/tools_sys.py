"""
    Created on 2012-01-27
    @author: jldupont
"""
import json, sys
import types
import logging


def info_dump(d, align):
    fmt="%-"+str(align)+"s : %s"

    if type(d)==types.DictionaryType:        
        for key in d:
            logging.info(fmt % (key, d[key]))
            
    if type(d)==types.ListType:
        for el in d:
            key, value=el
            logging.info(fmt % (key, value))


def stdout(s):
    sys.stdout.write(s+"\n")


def json_string(o):
    try:
        return json.dumps(o)
    except:
        return ""
