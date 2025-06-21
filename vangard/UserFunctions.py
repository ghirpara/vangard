"""
    UserConfig.py
 
   
 
    Author: G.Hirpara
    Version: 1.0.0
    Copyright (c) 2025 G.Hirpara
  
    LICENSING FOR THIS CODE IS DOCUMENTED IN THE ACCOMPANYING LICENSE.md FILE. 
    USERS OF THIS CODE AGREE TO TERMS AND CONDITIONS OUTLINED IN THE LICENSE.
  
"""

import json
import glob
from pathlib import Path
import os.path
import time

from .CommonUtils import common_logger

def extract_glob_to_list(scene_files):
    rv = {}
    globout = []
    if (scene_files != "_"):
        globout = glob.glob(scene_files, recursive=True)

    common_logger.debug(f"Extracted glob set = {globout}")

    rv['scene_files'] = globout
    return rv

