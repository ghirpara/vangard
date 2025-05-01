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

import os
import pathlib
from pathlib import Path
import sys
import subprocess
import argparse
import json 
import shutil
import tempfile
import datetime as dt
import time
from utils import exec_generic_command
from pathlib import Path
import logging
import shlex
import atexit

import pygments
from rich.console import Console # Import rich Console
from rich.markdown import Markdown # Import rich Markdown renderer
from typing import List, Dict, Any, Optional # For type hinting
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory # Optional: For persistent history
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory # Optional: Suggest based on history
from prompt_toolkit.completion import NestedCompleter

__iname__ = 'Daz Scene Commander'
__version__ = '1.0.0'

logger=None
script_location = Path(__file__).resolve().parent

# --- Prompt entry history
prompt_history_file = os.path.join(os.path.expanduser("~"), ".dazsu_history")
prompt_history = FileHistory(prompt_history_file)

## Define the history file path
#history_file = os.path.expanduser("~/.pythonhistory")

# Genericized Command file
command_map = json.load(open("commands.json", "r"))

# --- ANSI Color Codes (Optional - for the 'You:' prompt if not using rich for it) ---
supports_color = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
if supports_color:
    COLOR_COMMAND     = "\033[0;33m"
    COLOR_ARGS        = "\033[0;34m"  # Blue for the prompt prefix
    COLOR_RESET = "\033[0m"
else:
    COLOR_COMMAND     = ""
    COLOR_ARGS        = ""  # Blue for the prompt prefix
    COLOR_RESET       = ""

console=Console()

def parse_command(command:str) -> (str, str):

    script_file=None
    script_args=None

    parts = shlex.split(command)

    key = parts[0]

    if key == 'help':
        lines=[]
        for item in command_map:
            command=item
            cargs=[]
            for x in command_map[item]['args']:
                cargs.append (x['name'])

            arglist=" ".join(cargs)
            lines.append (f"{COLOR_COMMAND}{command}{COLOR_RESET} {COLOR_ARGS}{arglist}{COLOR_RESET}")


        print ("\n".join(lines))
        return None, None

    if key in command_map:
        command_object = command_map[key]
        script_file = f"{script_location}/{command_object['script_file']}"
        script_args=[]
        n=1
        for arg in command_object['args']:
            if n < len(parts):
                script_args.append (parts[n])
            n+=1

    return script_file, script_args

def _parse_command(command:str) -> (str, str):

    script_file=None
    script_args=None

    parts = shlex.split(command)

    if len(parts) > 0:

        command=parts[0].strip()

        if command == "transform-copy":
            if (len(parts) >= 3):
                script_file = f'{script_location}/TransformObjectSU.dsa'
                script_args = [parts[1].strip(), parts[2].strip()]
                if (len(parts) > 3):
                    script_args.append(parts[3:])
        elif command == "create-cam":
            script_file = f'{script_location}/CreateBasicCameraSU.dsa'
            cam_name = parts[1].strip()
            cam_class = parts[2].strip()
            if len(parts) > 3:
                do_focus = (parts[3].strip() == "focus")
            else:
                do_focus = False
            script_args = [cam_name, cam_class, do_focus]
        elif command == "create-group":
            script_file = f'{script_location}/CreateGroupNodeSU.dsa'
            script_args = [parts[1]];
        elif command == "help":
            print (
                """
                transform-copy
                create-cam
                create-group
                """
            )
                    
    return script_file, script_args

if __name__ == '__main__':

    parser = argparse.ArgumentParser (
        prog="DAZ Studio Razor",
        description="A batch submission script to manipulate and render a series of scene files to an iRay server instance, cluster, or farm."
    )

    parser.add_argument ('-d', '--debug', default=False, action='store_true')
    parser.add_argument ('-v', '--version', default=False, action='store_true')
    parser.add_argument ('-n', '--no-command', default=False, action='store_true')    

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    if (args.version):
        logger.info (f'{__iname__} {__version__}')
        sys.exit(0)

    console.print("Welcome to the Daz Scene Commander CLI")
    console.print ("   'exit' to quit)")

    while True:
        try:
            # Read input from the user
            command = prompt(
                ">",
                history=prompt_history,                   # Enable history
                auto_suggest=AutoSuggestFromHistory(), # Enable suggestions
                # enable_history_search=True,      # Enable Ctrl+R search (already default)
                # vi_mode=True                     # Uncomment for Vi keybindings instead of Emacs
            )   

            command = command.strip()

            if len(command.strip()) > 0:

                script_file, script_args = parse_command (command)

                if script_file is not None:

                    exec_generic_command (script_file,
                                          script_args,
                                          no_command = args.no_command)
            

        except (EOFError, KeyboardInterrupt):
            # Exit the loop on Ctrl+D or Ctrl+C
            #logger.error("\nExiting...")
            break
        except Exception as e:
            # Print any errors that occur
            logger.error(f"Error: {e}")

    
    
