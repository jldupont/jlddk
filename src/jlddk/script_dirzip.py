"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, os, tempfile, zipfile
from time import sleep
from tools_os import getsubdirs, rm, get_root_files, rmdir, handle_path


def run( polling=None
        ,dir_src=None
        ,dir_dst=None
        ,dir_tmp=None
        ,exit_error=False
        ,delete_source=False
        ,**_):

    dir_src=handle_path(dir_src)
    dir_dst=handle_path(dir_dst)
    dir_tmp=handle_path(dir_tmp)
    
    ppid=os.getppid()        
    logging.info("Process pid: %s" % os.getpid())
    logging.info("Parent pid:  %s" % ppid)
    logging.info("Starting loop...")
    
    while True:
        if os.getppid()!=ppid:
            logging.warning("Parent terminated... exiting")
            break
            
        do_processing(delete_source, exit_error, dir_src, dir_dst, dir_tmp)
        
        logging.debug("...sleeping for %s seconds" % polling)
        sleep(polling)



def do_processing(delete_source, exit_error, dir_src, dir_dst, dir_tmp):
    logging.debug("Processing BEGINS...")
    
    code, dirs=getsubdirs(dir_src)
    if not code.startswith("ok"):
        raise Exception("Can't get subdirectories of: %s" % dir_src)
    
    for d in dirs:
        try:
            bn_dir_src=os.path.basename(d)
        
            dfile_path=process_dir(delete_source, d, bn_dir_src, dir_dst, dir_tmp)
            
            logging.info("progress: Created archive: %s" % dfile_path)
            
        except Exception,e:
            m="Can't process directory %s (%s)" % (d, e)
            if exit_error:
                raise Exception(m)
            logging.warning(m)
        
    logging.debug("Processing ENDS...")
        

def process_dir(delete_source, 
                dir_src, 
                bn_dir_src, 
                dir_dst, 
                dir_tmp):
    logging.debug("Processing dir BEGIN: %s" % dir_src)

    zfile_path_tmp=tempfile.mktemp(dir=dir_tmp)
    
    logging.debug("Creating archive '%s'" % zfile_path_tmp)
    try:
        zfile=zipfile.ZipFile(zfile_path_tmp, "w")
        
        os.chdir(dir_src)
        
        code, files=get_root_files(dir_src, strip_dirname=True)
        if code!="ok":
            raise Exception("Can't get files from dir: %s" % dir_src)
        
        for fichier in files:
            zfile.write(fichier)
            
        zfile.close()
        
    except Exception, e:
        rm(zfile_path_tmp)
        raise Exception("Can't generate zip archive: %s (%s)" % (zfile_path_tmp, e))
    
    dfile_path=os.path.join(dir_dst, bn_dir_src+".zip")    
    logging.debug("Moving to %s" % dfile_path)
    
    os.rename(zfile_path_tmp, dfile_path)
    
    if delete_source:
        logging.debug("Deleting source subdir: %s" % dir_src)
        rmdir(dir_src)
    
    logging.debug("Processing dir ENDS: %s" % dir_src)
        
    return dfile_path
    
