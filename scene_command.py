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
from pathlib import Path
import logging
from scene_command_processor import SceneCommandProcessor

# Basic configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', handlers=[logging.FileHandler("razor.log")])

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
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    if (args.version):
        logging.info (f'{__iname__} {__version__}')
        sys.exit(0)

    scene_commander = SceneCommandProcessor(args.command_file)
    scene_commander.process_loop()



    
    
