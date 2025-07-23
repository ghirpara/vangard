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