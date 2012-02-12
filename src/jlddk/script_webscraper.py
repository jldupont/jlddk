"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, os
from time import sleep
from tools_web import fetch, parse, f_extract_href
from tools_func import coroutine, check_transition
from tools_sys import json_string, stdout
from tools_misc import batch

from pyfnc import dic, liste

def run(polling_interval=None, source_url=None, 
        batch_size=None,
        format_json=None, propagate_error=None, check_path=None):
    
    proc=process(source_url, propagate_error, format_json, batch_size)
    
    if check_path is not None:
        ct=check_transition()
    
    logging.info("Starting loop...")
    while True:
        
        if check_path is not None:
            try:    exists=os.path.exists(check_path)
            except: exists=False
            
            maybe_tr, _=ct.send(exists)
            if maybe_tr=="tr" and exists:
                logging.info("Check path: passed")
            if maybe_tr=="tr" and not exists:
                logging.info("Check path: failed - skipping")
        else:
            ## fake 'exists'
            exists=True
                

        if exists:            
            #########################################################
            status, (code, headers, data)=fetch(source_url)
            if status.startswith("ok"):
                proc.send((code, headers, data))
            else:
                if propagate_error:
                    stdout('''{"status":"error", "kind":"fetch", "source_url":"%s", "http_code":"%s"}''' % (source_url, code))
            #########################################################

        logging.debug("...sleeping for %s seconds" % polling_interval)
        sleep(polling_interval)
        
        
@coroutine
def process(source_url, propagate_error, format_json, batch_size):
    
    last_modified=None
    last_etag=None

    proc_l2=process_l2(source_url, propagate_error, format_json, batch_size)
    
    while True:
        code, headers, data=(yield)
        this_last_modified=headers.get("last-modified", None)
        this_etag=headers.get("etag", None)
        
        if last_etag!=this_etag or last_modified!=this_last_modified:
            proc_l2.send((code, headers, data))
            
        last_modified=this_last_modified
        last_etag=this_etag
        
@coroutine
def process_l2(source_url, propagate_error, format_json, batch_size):
    
    proc_l3=process_l3(source_url, propagate_error, format_json, batch_size)
    
    while True:
        http_code, headers, data=(yield)
        resp=parse(data)
        code_extract, hrefs=f_extract_href(resp)
        proc_l3.send(( (http_code, headers), (code_extract, hrefs) ))

@coroutine
def process_l3(source_url, propagate_error, format_json, batch_size):
    
    while True:
        ( (http_code, headers), (code_extract, hrefs) )=(yield)
        
        based={"source_url": source_url
           ,"http_status": http_code
           ,"etag": headers.get("etag", None)
           ,"last-modified": headers.get("last-modified", None)
           ,"extract_status": code_extract
           }

        for hrefs in batch(hrefs, batch_size):
            
            d=dic(based).update({"hrefs": hrefs})
                
            if format_json:
                stdout(json_string(d))
            else:
                if hrefs is not None:
                    for href in hrefs:
                        stdout(href)
                
