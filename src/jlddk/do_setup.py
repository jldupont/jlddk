"""
    @author: Jean-Lou Dupont
"""

import logging

FORMAT='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(FORMAT)

logging.basicConfig(level=logging.INFO, format=FORMAT)

