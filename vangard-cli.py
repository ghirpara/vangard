###################################################################
#
# Razor - Batch utilities for DAZ Studio 4.22+
#
# Copyright (c) 2024-present G.S. Hirpara <gsh@bluemoonfoundry.com>
#
# Licensed under the MIT License.
# See LICENSE in the project root for license information.
#
#
###################################################################

import sys
import argparse
import logging
from pathlib import Path
from vangard.SceneCommandProcessor import SceneCommandProcessor
from vangard.CommonUtils import common_logger


__iname__ = 'Daz Scene Commander'
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
    parser.add_argument ('-c', '--command-file', default="commands.json")
    args = parser.parse_args()

    if args.debug:
        common_logger.setLevel(logging.DEBUG)
    else:
        common_logger.setLevel(logging.INFO)
    
    if (args.version):
        common_logger.info (f'{__iname__} {__version__}')
        sys.exit(0)

    scene_commander = SceneCommandProcessor(args.command_file)
    scene_commander.process_loop()



    
    
