"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, sys, os, json
from tools_os import atomic_write, can_write
from tools_logging import setloglevel
from tools_web import fetch


def run(dest_path=None, 
        loglevel="info", logconfig=None):
    
    if logconfig is not None:
        logging.config.fileConfig(logconfig)

    setloglevel(loglevel)

    if dest_path is not None:
        if not os.path.isdir(dest_path):
            raise Exception("Expecting a valid destination path '%s'" % dest_path)
            
    logging.info("Starting loop...")
    while True:
        
        iline=sys.stdin.readline().strip()
        
        #################### VALIDATE
        ## if we received two strings on the same line:  url  dst_path
        bits=iline.split(" ")
        l=len(bits)
        if l > 2 or l==0:
            logging.error("Invalid input line: %s" % iline)
            continue
        
        url=bits[0]
        bn=os.path.basename(url)
        
        if len(bits)==2:
            path=bits[1]
        else:
            if dest_path is not None:
                path=os.path.join(dest_path, bn)
            else:
                logging.warning("Didn't receive 'dest_path' from stdin and none specified on command line...")
                continue
            
        ####### WRITE CAPABILITY VERIFICATION
        code, result=can_write(path)
        if not code.startswith("ok") or not result:
            logging.warning("Won't be able to write to path '%s'... skipping download" % path)
            continue
            
        ####### DOWNLOAD
            
        code, (http_code, headers, data)=fetch(url)
        if not code.startswith("ok"):
            logging.warning("Error attempting to download: %s" % url)
            continue
        
        try:     http_code=int(http_code)
        except:  pass
        
        if http_code!=200:
            logging.warning("Can't fetch url '%s', http response code: %s" % (url, http_code))
            continue
                        
        code, msg=atomic_write(path, data)
        if not code.startswith("ok"):
            raise Exception("Can't write to file '%s': %s" % (path, msg))
        
        ctx={
             "dest_filename": path
             ,"url": url
             ,"http_code": http_code
             ,"headers": headers
             }
        
        try:    sys.stdout.write(json.dumps(ctx)+"\n")
        except: pass
            
        

            