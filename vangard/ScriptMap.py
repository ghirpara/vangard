"""
    ScriptMap.py
 
   
 
    Author: G.Hirpara
    Version: 1.0.0
    Copyright (c) 2025 G.Hirpara
  
    LICENSING FOR THIS CODE IS DOCUMENTED IN THE ACCOMPANYING LICENSE.md FILE. 
    USERS OF THIS CODE AGREE TO TERMS AND CONDITIONS OUTLINED IN THE LICENSE.
  
"""

import os
from pathlib import Path

from CommonUtils import common_logger
from RazorConfig import RazorConfig


class ScriptMap:

    def __init__(self, config:RazorConfig):
        self.config = config
        self.script_map = {}

        script_dir = Path(__file__).resolve().parent

        self.script_locations = [
            f"{script_dir}/../dazscripts"
        ]

        for alt in self.config.get("alt_script_locations", []):
            self.script_locations.append(alt)


    def add_script_mapping(self, script_name, script_dir=None):
        if script_dir is not None:
             if script_dir not in self.script_locations:
                    self.script_locations.append(script_dir)

        for key in self.script_locations:
            test = f"{key}/{script_name}"
            if (os.path.exists(test)):
                self.script_map[script_name] = test
                common_logger.info (f"Added script {script_name} = {test}")
            else:
                common_logger.error (f"Could not locate script {test}. Make sure path exists and is readable.")

    def get_script_mapping(self, script_name):
        return self.script_map.get(script_name, None)