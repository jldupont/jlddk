"""
    @author: Jean-Lou Dupont
"""

import sys,os
from tools_logging import setup_basic_logging


## force stdout flushing
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)

setup_basic_logging()
