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

import sys
import argparse
import logging
from pathlib import Path
#from vangard.SceneCommandProcessor import SceneCommandProcessor
from vangard.CommandProcessor import CommandProcessor
from vangard.CommonUtils import common_logger


__iname__ = 'Daz Scene Commander CLI'
__version__ = '1.0.0'

logger=None

if __name__ == '__main__':

    parser = argparse.ArgumentParser (
        prog="DAZ Studio CLI Utilities",
        description="A script for common DAZ Studio utility functions from a command-line."
    )

    parser.add_argument ('-d', '--debug', default=False, action='store_true')
    parser.add_argument ('-v', '--version', default=False, action='store_true')
    parser.add_argument ('-n', '--no-command', default=False, action='store_true')    
    parser.add_argument ('-c', '--command-file', default="config.json")
    args = parser.parse_args()

    if args.debug:
        common_logger.setLevel(logging.DEBUG)
    else:
        common_logger.setLevel(logging.INFO)
    
    if (args.version):
        common_logger.info (f'{__iname__} {__version__}')
        sys.exit(0)

    #scene_commander = SceneCommandProcessor(args.command_file)
    #scene_commander.process_loop()

    processor = CommandProcessor(args.command_file)
    processor.run()




    

    
