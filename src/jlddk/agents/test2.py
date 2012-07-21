"""
    Created on 2012-07-21
    @author: jldupont
"""
import logging


def init(_q, *p):
    print "test2.init", p

def tick(_q, _):
    logging.info("test2: tick!")



__vtable__={"init": init, "tick": tick}    