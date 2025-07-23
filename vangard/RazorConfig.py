# Copyright (C) 2025 Blue Moon Foundary Software
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
from pathlib import Path
import json

from .CommonUtils import common_logger

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