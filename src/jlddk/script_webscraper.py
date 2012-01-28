"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging
from time import sleep
from tools_web import fetch, parse, f_extract_href
from tools_func import coroutine
from tools_sys import json_string, stdout, info_dump

def run(args):
    
    ## shortcuts
    polling_interval=args.polling_interval
    source_url=args.source_url.strip()
    format_json=args.format_json
    propagate_error=args.propagate_error
    
    info_dump(vars(args), 20)
    
    proc=process(source_url, propagate_error, format_json)
    
    logging.info("Starting loop...")
    while True:
        
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
def process(source_url, propagate_error, format_json):
    
    last_modified=None
    last_etag=None

    proc_l2=process_l2(source_url, propagate_error, format_json)
    
    while True:
        code, headers, data=(yield)
        this_last_modified=headers.get("last-modified", None)
        this_etag=headers.get("etag", None)
        
        if last_etag!=this_etag or last_modified!=this_last_modified:
            proc_l2.send((code, headers, data))
            
        last_modified=this_last_modified
        last_etag=this_etag
        
@coroutine
def process_l2(source_url, propagate_error, format_json):
    
    proc_l3=process_l3(source_url, propagate_error, format_json)
    
    while True:
        http_code, headers, data=(yield)
        resp=parse(data)
        code_extract, hrefs=f_extract_href(resp)
        proc_l3.send(( (http_code, headers), (code_extract, hrefs) ))

@coroutine
def process_l3(source_url, propagate_error, format_json):
    
    while True:
        ( (http_code, headers), (code_extract, hrefs) )=(yield)
        
        d={"source_url": source_url
           ,"http_status": http_code
           ,"etag": headers.get("etag", None)
           ,"last-modified": headers.get("last-modified", None)
           ,"extract_status": code_extract
           ,"hrefs": hrefs
           }
        
        if format_json:
            stdout(json_string(d))
        else:
            if hrefs is not None:
                for href in hrefs:
                    stdout(href)
                
        


