
import os
import logging
from pathlib import Path
from razor_config import RazorConfig

from glogger import glogger

class ScriptMap:

    def __init__(self, config:RazorConfig):
        self.config = config
        self.script_map = {}

        script_dir = Path(__file__).resolve().parent  

        self.script_locations = [
            f"{script_dir}/dazscripts"
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
                glogger.info (f"Added script {test}")
            else:
                glogger.error (f"Could not locate script {test}. Make sure path exists and is readable.")

    def get_script_mapping(self, script_name):
        return self.script_map.get(script_name, None)


