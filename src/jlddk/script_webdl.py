"""
    Created on 2012-01-27
    @author: jldupont
"""
import logging, sys, os
from time import sleep
from tools_os import mkdir_p, get_root_files
from tools_logging import setloglevel


def run(source_path=None, dest_path=None, batch_size=5, loglevel="info", logconfig=None, polling_interval=None):
    
    if logconfig is not None:
        logging.config.fileConfig(logconfig)

    setloglevel(loglevel)

    logging.info("Creating (if necessary) destination path: %s" % dest_path)
    code, msg=mkdir_p(dest_path)
    if not code.startswith("ok"):
        raise Exception("Can't create destination path '%s': %s" % (dest_path, str(msg)))
            
    logging.info("Starting loop...")
    while True:
        
        code, files=get_root_files(source_path)
        if not code.startswith("ok"):
            logging.error("Can't get root files from %s" % source_path)
            continue
        
        files=files[:batch_size]
        try:
            for phile in files:
                process(file, dest_path)
        except Exception, e:
            logging.error("processing file '%s': %s" % (phile, str(e)))
        
        
        logging.debug("...sleeping for %s seconds" % polling_interval)
        sleep(polling_interval)


def process(phile, dest_path):
    """
    1. read file, extract URL
    2. fetch file from URL
    3. write fetched file to dest_path
    4. delete pointer file
    """
    