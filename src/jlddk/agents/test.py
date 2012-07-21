"""
    Created on 2012-07-21
    @author: jldupont
"""
import logging
from time import sleep



def init(mqueue, _msg):
    mqueue.append({"topic": "tick"})

def tick(mqueue, _):
    logging.info("test: tick!")
    sleep(1)
    mqueue.append({"topic": "tick"})



__vtable__={"init": init, "tick": tick}    