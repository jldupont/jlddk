"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, sys, json, os
from time import sleep
from tools_os import mkdir_p, get_root_files, file_contents
from tools_os import rm, can_write, resolve_path, move
from tools_logging import setloglevel
from tools_func import check_transition

def stdout(jo):
    sys.stdout.write(json.dumps(jo)+"\n")

class BrokenPipe(Exception): pass


def run(source_path=None, move_path=None, check_path=None, 
        batch_size=5, loglevel="info", logconfig=None, polling_interval=None, enable_delete=False):

    if check_path is not None:
        ct=check_transition()

    if logconfig is not None:
        logging.config.fileConfig(logconfig)

    setloglevel(loglevel)

    if enable_delete and move_path is not None:
        raise Exception("Options '-mp' and '-d' are mutually exclusive")
        
    code, rp=resolve_path(source_path)
    if not code.startswith("ok"):
        raise Exception("can't resolve source path '%s'" % source_path)
    source_path=rp
    
    if move_path is not None:
        code, rp=resolve_path(move_path)
        if not code.startswith("ok"):
            raise Exception("can't resolve 'move_path' '%s'" % move_path)
        move_path=rp

        logging.info("Creating (if necessary) 'move' path: %s" % move_path)
        code, msg=mkdir_p(move_path)
        if not code.startswith("ok"):
            raise Exception("Can't create move path '%s': %s" % (move_path, str(msg)))
            
        logging.info("Checking if 'move' directory is writable")
        code, msg=can_write(move_path)
        if not code.startswith("ok"):
            raise Exception("Can't write to 'move' directory")
            
    to_skip=[]
    logging.info("Process pid: %s" % os.getpid())
    ppid=os.getppid()
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
            else:                
                ###############################################################
                files=files[:batch_size]
                try:
                    for src_file in files:
                        
                        if src_file in to_skip:
                            continue
                        
                        code, _=can_write(src_file)
                        if not code.startswith("ok"):
                            to_skip.append(src_file)
                            logging.error("Would not be able to move/delete source file '%s'... skipping streaming" % src_file)
                            continue
        
                        dst_file=None                
                        if move_path is not None:
                            bn=os.path.basename(src_file)
                            dst_file=os.path.join(move_path, bn)
                        
                        code, maybe_error=process(src_file, dst_file, enable_delete)
                        if not code.startswith("ok"):
                            to_skip.append(src_file)
                            logging.warning("Problem processing file '%s': %s" % (src_file, maybe_error))
                except BrokenPipe:
                    raise
                except KeyboardInterrupt:
                    raise
                except Exception, e:
                    logging.error("processing file '%s': %s" % (src_file, str(e)))
                ###############################################################            
        
        
        logging.debug("...sleeping for %s seconds" % polling_interval)
        sleep(polling_interval)


def process(src_file, dst_file, enable_delete):
    """
    1. read file, extract URL
    2. send "start"
    3. send each line
    4. send "end"
    5. move/delete source file
    """
    code, contents=file_contents(src_file)
    if not code.startswith("ok"):
        return ("error", "file/invalid")
    
    try:    
        contents=contents.strip()
        lines=contents.split("\n")
    except:
        return ("error", "data/invalid")
    
    ###############################################
    try:
        stdout({"sp": src_file, "code":"begin"})    
        for line in lines:
            stdout({"code": "line", "line": line})
        stdout({"sp": src_file, "code":"end"})
    except:
        raise BrokenPipe("Broken Pipe")
    ###############################################
    
        
    if enable_delete:
        code, _msg=rm(src_file)
        if not code.startswith("ok"):
            logging.error("Can't delete '%s'" % src_file)
            return ("error", "file/delete")
        return ("ok", None)
    
    ### well then, we need to move the source_file
    code, _=move(src_file, dst_file)
    return (code, "file/move")

