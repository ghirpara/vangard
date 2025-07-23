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

