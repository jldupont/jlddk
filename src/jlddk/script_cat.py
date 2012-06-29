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
        check_done=None,
        gen_done=None,  
        ignore_fault=False,
        verbose=False,
        rm_ext=False
        ,loglevel=None
        ,**_
        ):
    
    
    
    maybe_log(verbose, "Resolving path for: %s" % path_source)
    try:
        apath=os.path.abspath(path_source)
        spath=apath.strip("\"'")
        spath=os.path.expanduser(os.path.expandvars(spath))
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
        
        if check_done:
            exists=os.path.exists(_file+".done")
            if exists:
                maybe_log(verbose, "File '%s' already processed... skipping" % _file)
                continue
            
        try:
            maybe_log(verbose, "Processing '%s'" % _file)
            process_file(verbose, ignore_fault, rm_ext, _file)
        except Exception,e:
            if not ignore_fault:
                raise Exception("Can't process '%s': %s" % (_file, e))
            
        if gen_done:
            result, _=touch(_file+".done")
            if not result.startswith("ok"):
                if not ignore_fault:
                    raise Exception("Can't write 'done' file in source path")
            else:
                maybe_log(verbose, "Wrote 'done' file for: %s" % _file)
    
    
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
    
        
        
    
    