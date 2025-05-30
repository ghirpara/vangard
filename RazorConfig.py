from CommonLogger import common_logger


import json
import os
from pathlib import Path


class RazorConfig:

    def __init__(self, filename, default_config):

        self.config = default_config
        self.config_file_path = None

        script_dir = Path(__file__).resolve().parent
        home_dir   = str(Path.home())

        config_file_locations = [
            f"{home_dir}/.{filename}",
            f"{home_dir}/{filename}",
            f"{script_dir}/{filename}",
            f"{script_dir}/{filename}"
        ]

        cfile_path = None
        for x in config_file_locations:
            if (os.path.exists(x)):
                cfile_path = x
                break

        if (cfile_path is not None):
            self.config_file_path = cfile_path
            self.config = json.load(open(cfile_path, "r"))

        common_logger.debug(f"Extracted Razor configuration is\n{json.dumps(self.config, indent=2)}")


    def get(self, key, default_value=None):
        return self.config.get(key, default_value)