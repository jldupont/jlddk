"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, os, tempfile
from time import sleep
from tools_os import move, getsubdirs, rm, get_root_files, rmdir, handle_path


def run( polling=None
        ,ext_done=None
        ,dir_src=None
        ,dir_dst=None
        ,dir_tmp=None
        ,del_dir_dst=False
        ,mode_dir=False
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
            
        do_processing(ext_done, mode_dir, del_dir_dst, dir_src, dir_dst, dir_tmp)
        
        logging.debug("...sleeping for %s seconds" % polling)
        sleep(polling)



def do_processing(ext_done, mode_dir, del_dir_dst, dir_src, dir_dst, dir_tmp):
    logging.debug("Processing starts...")
    
    code, dirs=getsubdirs(dir_src)
    if not code.startswith("ok"):
        raise Exception("Can't get subdirectories of: %s" % dir_src)
    
    for d in dirs:
        if mode_dir:
            bn_dir_src=os.path.basename(d)
            if not bn_dir_src.endswith(ext_done):
                continue
        
        process_dir(ext_done, mode_dir, del_dir_dst, d, bn_dir_src, dir_dst, dir_tmp)
        
    logging.debug("Processing ends...")
        

def process_dir(ext_done, mode_dir, del_dir_dst, dir_src, bn_dir_src, dir_dst, dir_tmp):
    logging.debug("Processing dir: %s" % dir_src)
    
    if not mode_dir:
        code, maybe_files=get_root_files(dir_src, strip_dirname=True)
        if not code.startswith("ok"):
            raise Exception("Can't get the filenames of dir: %s" % dir_src)
        
        for f in maybe_files:
            if not f.endswith(ext_done):
                df="%s.%s" % (f, ext_done)
                if not df in maybe_files:
                    logging.debug("Missing 'done' file for: %s" % f)
                    return
    
    do_move(mode_dir, ext_done, del_dir_dst, dir_src, bn_dir_src, dir_dst, dir_tmp)
    
    
    
def do_move(mode_dir, ext_done, del_dir_dst, dir_src, bn_dir_src, dir_dst, dir_tmp):
    """
    - Move path directory to a temporary dir in 'dir_tmp'
    - Delete 'file.ext_done' files
    - Move path directory to 'dir_dst'
    """
    dpath, tdir, tpath=do_common(mode_dir, bn_dir_src, del_dir_dst, dir_src, dir_dst, dir_tmp)
    
    if not mode_dir: 
        
        ## next, delete all files with extension 'ext_done'
        code, maybe_files=get_root_files(tpath)
        if not code.startswith("ok"):
            rmdir(tdir)
            raise Exception("Can't get the filenames of temp dir: %s" % tpath)
        
        def _cmp(path):
            return path.endswith(ext_done)
        
        liste=filter(_cmp, maybe_files)
        
        logging.debug("Deleting '%s' files with extension '%s'" % (len(liste), ext_done))
        for f in liste:
            code, _=rm(f)
            if not code.startswith("ok"):
                logging.warning("Can't delete file '%s'... aborting" % f)
                rmdir(tdir)
                return
    
    ## last, move to final destination
    
    logging.debug("Moving '%s' to final dir '%s'" % (tpath, dpath))
    code, _=move(tpath, dpath)
    rmdir(tdir)
    logging.debug("Removed temp dir: %s" % tdir)
    if not code.startswith("ok"):
        raise Exception("Can't move '%s' to directory" % dpath)
    
    logging.info("Processed directory: %s" % dir_src)


def do_common(mode_dir, bn_dir_src, del_dir_dst, dir_src, dir_dst, dir_tmp):
    
    dpath=maybe_del_dir(mode_dir, del_dir_dst, bn_dir_src, dir_dst)
    
    try:
        tdir=tempfile.mkdtemp(dir=dir_tmp)
    except:
        raise Exception("Can't create temporary directory")
    
    tpath=os.path.join(tdir, bn_dir_src)
    
    ## rename
    if mode_dir:
        tpath=os.path.splitext(tpath)[0]
    
    logging.debug("Moving to temp dir: %s => %s" % (dir_src, tpath))
    code, _=move(dir_src, tpath)
    if not code.startswith("ok"):
        rm(tdir)
        raise Exception("Can't move '%s' in a temp directory" % tpath)

    return dpath, tdir, tpath
        
    
    
def maybe_del_dir(mode_dir, del_dir_dst, bn_dir_src, dir_dst):

    dpath=os.path.join(dir_dst, bn_dir_src)
    if mode_dir:
        dpath=os.path.splitext(dpath)[0]
    
    if del_dir_dst:
        logging.debug("Deleting destination directory: %s" % dpath)
        rmdir(dpath)

    return dpath
