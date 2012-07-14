"""
    Created on 2012-01-27
    @author: jldupont
"""
import os, glob, logging
from jlddk.tools_os import file_contents, touch

def maybe_log(verbose, msg):
    if verbose:
        logging.info(msg)
    

def run(path_source=None,
        path_done=None,
        check_done=None,
        gen_done=None,  
        ignore_fault=False,
        verbose=False,
        rm_ext=False
        ,**_
        ):
    
    if check_done and path_done is None:
        raise Exception("Must specify 'done path'")
    
    maybe_log(verbose, "Resolving path for: %s" % path_source)
    try:
        apath=os.path.abspath(path_source)
        spath=apath.strip("\"'")
        spath=os.path.expanduser(os.path.expandvars(spath))
    except:
        raise Exception("Can't resolve path")

    dpath=None
    if check_done:
        maybe_log(verbose, "Resolving path for done files: %s" % path_done)
        try:
            dpath=os.path.abspath(path_done)
            dpath=dpath.strip("\"'")
            dpath=os.path.expanduser(os.path.expandvars(dpath))
        except:
            raise Exception("Can't resolve path")
        

    try:    
        files=glob.glob(os.path.join(spath, "*"))
    except:
        raise Exception("Can't fetch files")
    
    ## strip directories
    files=filter(os.path.isfile, files)
    
    for _file in files:
        
        if _file.endswith(".done"):
            continue
        
        bn=os.path.basename(_file)
        
        if check_done:
            pbn=os.path.join(dpath, bn)
            exists=os.path.exists(pbn+".done")
            if exists:
                maybe_log(verbose, "File '%s' already processed... skipping" % bn)
                continue
            
        try:
            maybe_log(verbose, "Processing '%s'" % bn)
            process_file(verbose, ignore_fault, rm_ext, _file)
        except Exception,e:
            if not ignore_fault:
                raise Exception("Can't process '%s': %s" % (bn, e))
            
        if gen_done:
            done_file=os.path.join(dpath, bn)
            result, _=touch(done_file+".done")
            if not result.startswith("ok"):
                if not ignore_fault:
                    raise Exception("Can't write 'done' file in 'done' path")
            else:
                maybe_log(verbose, "Wrote 'done' file for: %s" % bn)
    
    
def process_file(verbose, ignore_fault, rm_ext, _file):
    
    result, contents=file_contents(_file)
    if not result.startswith("ok"):
        if not ignore_fault:
            raise Exception("Can't read file: %s" % _file)
    
    try:    
        maybe_log(verbose, "Formatting file contents")
        contents=contents.replace('\t', ' ')
        lines=contents.split("\n")
        big_line='\t'.join(lines)
        
        name=os.path.basename(_file)
        if rm_ext:
            name, _=os.path.splitext(name)
        whole_line="%s\t%s" % (name, big_line)
    except:
        raise Exception("Can't format text file")
    
    maybe_log(verbose, "Outputting file")
    print whole_line
    
        
        
    
    