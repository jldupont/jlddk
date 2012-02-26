"""
    Created on 2012-01-27
    @author: jldupont
    
    Generates the following JSON object upon success:
    
        ctx={
         "dest_filename": dest_filename
         ,"src_filename": src_file
         ,"url": url
         ,"http_code": http_code
         ,"headers": headers
         }

    
"""
import logging, sys, os, uuid, json, select, time 

from tools_os import mkdir_p, get_root_files, file_contents
from tools_os import rm, can_write, atomic_write
from tools_logging import setloglevel
from tools_web import fetch, extract_url_filename
from tools_func import check_transition

class BrokenPipe(Exception): pass


def run(source_path=None, dest_path=None, check_path=None, 
        batch_size=5, loglevel="info", logconfig=None, polling_interval=None, delete_fetch_error=False):
    
    if check_path is not None:
        ct=check_transition()
    
    if logconfig is not None:
        logging.config.fileConfig(logconfig)

    setloglevel(loglevel)

    logging.info("Creating (if necessary) destination path: %s" % dest_path)
    code, msg=mkdir_p(dest_path)
    if not code.startswith("ok"):
        raise Exception("Can't create destination path '%s': %s" % (dest_path, str(msg)))
            
    to_skip=[]
    ppid=os.getppid()
    logging.info("Process pid: %s" % os.getpid())
    logging.info("Parent pid : %s" % ppid)
    logging.info("Starting loop...")
    while True:
        if os.getppid()!=ppid:
            logging.warning("Parent terminated... exiting")
            break
        
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
            code, files=get_root_files(source_path)
            if not code.startswith("ok"):
                logging.error("Can't get root files from %s" % source_path)
                continue
            
            ###############################################################
            files=files[:batch_size]
            try:
                for src_file in files:
                    
                    if src_file in to_skip:
                        continue
                    
                    code, _=can_write(src_file)
                    if not code.startswith("ok"):
                        to_skip.append(src_file)
                        logging.error("Would not be able to delete source file '%s'... skipping download" % src_file)
                        continue
                    
                    process(src_file, dest_path, delete_fetch_error)
            except BrokenPipe:
                raise
            except Exception, e:
                logging.error("processing file '%s': %s" % (src_file, str(e)))
            ###############################################################            
        
        
        logging.debug("...waiting for %s seconds (max)" % polling_interval)
        
        ### Implement a "pass-through" for stdin --> stdout
        ###  whilst also handling a maximum time-out
        start_time=time.time()
        while True:
            ir, _w, _e=select.select([sys.stdin], [], [], polling_interval)
            if len(ir):
                iline=sys.stdin.readline()
                sys.stdout.write(iline)
                
            elapsed_time = time.time() - start_time
            if elapsed_time > polling_interval:
                break
            
            


def process(src_file, dest_path, delete_fetch_error):
    """
    1. read file, extract URL
    2. fetch file from URL
    3. write fetched file to dest_path
    4. delete pointer file
    """
    code, contents=file_contents(src_file)
    if not code.startswith("ok"):
        logging.error("Can't read file contents from '%s'" % src_file)
        return
    
    try:    
        url=contents.strip()
    except: 
        raise Exception("Invalid data in file: %s" % src_file)
    
    
    code, (http_code, headers, data)=fetch(url)
    if not code.startswith("ok"):
        if delete_fetch_error:
            code, _msg=rm(src_file)
            logging.warning("Attempting to delete source file '%s': %s" % (src_file, code))
        raise Exception("Can't fetch page from url: %s" % url)

    try:     http_code=int(http_code)
    except:  pass
    
    if http_code!=200:
        logging.error("Can't fetch url '%s', http response code: %s" % (url, http_code))
        return

    code, maybe_components=extract_url_filename(url)
    if not code.startswith("ok"):
        fbn=str(uuid.uuid1())
        dest_filename=os.path.join(dest_path, fbn)
    else:
        fbn, fext=maybe_components
        dest_filename=os.path.join(dest_path, fbn)+fext

    try:    exists=os.path.exists(dest_filename)
    except: exists=False
        
    if exists:
        fbn=str(uuid.uuid1())
        dest_filename=os.path.join(dest_path, fbn)
        
    code, msg=atomic_write(dest_filename, data)
    if not code.startswith("ok"):
        raise Exception("Can't write to file '%s': %s" % (dest_filename, msg))
    
    ctx={
         "dest_filename": dest_filename
         ,"src_filename": src_file
         ,"url": url
         ,"http_code": http_code
         ,"headers": headers
         }
    
    ### no need
    code, msg=rm(src_file)
    if not code.startswith("ok"):
        logging.error("Can't delete '%s' : will probably cause excessive downloads..." % src_file)
    
    
    try:    sys.stdout.write(json.dumps(ctx)+"\n")
    except: 
        raise BrokenPipe()

