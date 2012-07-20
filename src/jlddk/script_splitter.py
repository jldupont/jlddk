"""
    Created on 2012-01-27
    @author: jldupont
"""
import os, logging, glob
from jlddk.tools_os import atomic_write, mkdir_p, file_contents, rm
from time import sleep

class ExpOK(Exception): pass
class ExpWarning(Exception): pass

def run(
        path_dest=None
        ,path_src=None
        ,file_output_ext=None
        ,file_input_pattern=None
        ,poll_interval=None
        ,start_of_file=None
        ,delete_source_dir=False
        ,**_
        ):
    
    start_of_file=start_of_file.strip("'\"")
    
    file_output_ext=file_output_ext.strip(".'\"")
    logging.info("Using '%s' as output file extension" % file_output_ext)

    ## SOURCE
    logging.info("Resolving source path: %s" % path_src)
    try:
        apath=os.path.abspath(path_src)
        spath=apath.strip("\"'")
        spath=os.path.expanduser(os.path.expandvars(spath))
    except:
        raise Exception("Can't source resolve path")
    
    logging.info("Resolve source path: %s" % spath)
    logging.info("Creating source, if required...")
    mkdir_p(spath)

    ## DESTINATION
    logging.info("Resolving destination path: %s" % path_dest)
    try:
        apath=os.path.abspath(path_dest)
        dpath=apath.strip("\"'")
        dpath=os.path.expanduser(os.path.expandvars(dpath))
    except:
        raise Exception("Can't resolve destination path")
        
    logging.info("Resolve destination path: %s" % dpath)
    logging.info("Creating destination, if required...")
    mkdir_p(dpath)

    def filter_tilde(path):
        return not path.startswith("~")

    ppid=os.getppid()        
    logging.info("Process pid: %s" % os.getpid())
    logging.info("Parent pid:  %s" % ppid)
    logging.info("Starting loop...")
    while True:
        if os.getppid()!=ppid:
            logging.warning("Parent terminated... exiting")
            break

        try:            
            try:
                dirs=os.listdir(spath)
                logging.debug("Dirs: %s" % len(dirs))
            except:
                raise ExpWarning("Can't get subdirectories of source path...")
            
            try:
                fdirs=filter(filter_tilde, dirs)
                logging.debug("Filtered dirs: %s" % len(fdirs))
            except:
                raise ExpWarning("Can't apply filter for ~dir...")
            
            if len(fdirs)==0:
                logging.debug("No directories to work on")
                raise
            
            wdir=os.path.join(spath, fdirs[0])
            logging.info("Progress> working on path: %s" % wdir)
            
            try:
                files=glob.glob(wdir+os.path.sep+file_input_pattern)
                files=filter(os.path.isfile, files)
                logging.debug("Got %s file(s) in selected dir" % len(files))
            except:
                raise ExpWarning("Can't glob files...")
            
            for _file in files:
                logging.debug("Processing '%s'" % _file)
                num_files=process(dpath, _file, start_of_file)
                logging.info("Progress> processed 1 concatenated file with '%s' files" % num_files)
                
            logging.info("Progress> processed %s files" % len(files))
            
            if delete_source_dir:
                logging.info("Deleting source directory: %s" % wdir)
                rm(wdir)
            
        except ExpWarning,e:
            logging.warning(e)
            
        except ExpOK,e:
            logging.info(e)
        
        logging.debug("Sleeping for %s seconds..." % poll_interval)
        sleep(poll_interval)    
        

def process(dpath, _file, start_of_file):
    
    bn=os.path.basename(_file)
    odir=os.path.join(dpath, bn)
    
    odirtemp=os.path.join(dpath, "~"+bn)
    logging.info("Creating output temporary directory name: %s" % odirtemp)
    code, _=mkdir_p(odirtemp)
    
    if not code.startswith("ok"):
        raise ExpWarning("Can't create temporary output directory: %s" % odirtemp)
    
    try:
        logging.debug("Getting file contents for: %s" % _file)
        code, contents=file_contents(_file)
        if not code.startswith("ok"):
            raise
    except:
        raise ExpWarning("Can't get file contents: %s" % _file)

    contents=contents.split("\n")
    logging.debug("File contains %s lines" % len(contents))
    buf=[]
    index=0
    for line in contents:
        if line.startswith(start_of_file):
            write_file(index, buf, bn, odirtemp)
            buf=[line,]           
            index=index+1
            continue
        else:
            buf.append(line)
            
    write_file(index, buf, bn, odirtemp)
    
    logging.info("Renaming directory... %s => %s" % (odirtemp, odir))
    try:
        os.rename(odirtemp, odir)
    except:
        raise ExpWarning("Can't rename %s => %s" % (odirtemp, odir))
    
    return index
        
        
def write_file(index, buf, bn, dpath):
    if len(buf)==0:
        return
    
    fn=bn+"_"+str(index)
    logging.debug("Writing file %s => %s" % (index, fn))
    
    contents="\n".join(buf)
    
    fp=os.path.join(dpath, fn)
    code, _=atomic_write(fp, contents)
    if not code.startswith("ok"):
        raise ExpWarning("Can't write to %s" % fp)

    logging.debug("Wrote file %s" % fp)
    

