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
import user_functions
from utils import exec_remote_script
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
import builtins

__iname__ = 'Daz Scene Commander'
__version__ = '1.0.0'

logger=None
script_location = str(Path(__file__).resolve().parent)+"/dazscripts"

# --- Prompt entry history
prompt_history_file = os.path.join(os.path.expanduser("~"), ".dazsu_history")
prompt_history = FileHistory(prompt_history_file)

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

command_map=None

type_dict = {
    'int': int,
    'float': float,
    'str': str,
    'list': list,
    'dict': dict,
    'bool': bool
}

def parse_command_file(command_file_name:str):
    command_map=json.load(open(command_file_name, 'r'))
    for key in command_map:
        command = command_map[key]
        parser = argparse.ArgumentParser(
            description=command['description'],
            prog=key
        )
        for arg in command['args']:
            names=None
            nv=arg['name']
            if isinstance(nv, str):
                names=[nv]
            elif isinstance(nv, list):
                names=nv

            kwargs={
                'default': arg['default'], 
                'help': arg['description']
            }

            if 'required' in arg:
                kwargs['required'] = arg['required']

            if arg['type'] == 'bool':
                kwargs['action']='store_true'
            else:
                kwargs['type'] = type_dict[arg['type'].strip()]
                kwargs['action']='store'

            parser.add_argument(
                *names,
                **kwargs
            )
            
            #     type=getattr(builtins, arg['type']), 
            #     required=arg['required'], 
            #     default=arg['default'], 
            #     help=arg['description']
            # )
        command['parser']=parser    
    return command_map        

def parse_command(command:str) -> tuple[list, list, str, Any, dict]:

    script_file=None
    script_args=None
    script_vars=None

    parts = shlex.split(command)

    key = parts[0]

    if key == 'help':
        lines=[]
        if len(parts) > 1:
            key = parts[1]
            command = command_map.get(key, None)
            if command is None:
                lines.append(f'Unknown command specified: {COLOR_COMMAND}{key}{COLOR_RESET}')
            else:
                usage_str=command['parser'].format_usage()
                parts=shlex.split(usage_str)
                cli_line = f"{COLOR_COMMAND}{parts[1]} {COLOR_RESET}{COLOR_ARGS}{' '.join(parts[2:])}{COLOR_RESET}"
                lines.append (cli_line)
                help_str=command['parser'].format_help()
                lines.append (help_str)

        else:
 
            for key in command_map:
                command=command_map[key]
                usage_str=command['parser'].format_usage()
                parts=shlex.split(usage_str)
                cli_line = f"{COLOR_COMMAND}{parts[1]} {COLOR_RESET}{COLOR_ARGS}{' '.join(parts[2:])}{COLOR_RESET}"
                lines.append (cli_line)


        print ("\n".join(lines))
        return None, None, None, None, None

    if key in command_map:
        command_object = command_map[key]
        script_file = f"{script_location}/{command_object['script-file']}"
        script_args=[]
        pre_scripts = command_object.get('pre-scripts')
        post_scripts = command_object.get('post-scripts')
        parser=command_object['parser']
        command_line=" ".join(parts[1:])
        script_args = parser.parse_args(parts[1:])
        script_vars = vars(script_args)

    return pre_scripts, post_scripts, script_file, script_args, script_vars

def exec_local_commands(scripts):
    if scripts is not None:
        for script in scripts:                      
            kargs={}
            for arg in script["script-args"]:
                kargs[arg]=script_vars[arg]
                callback=getattr(user_functions, script["script-callback"])
                callback(**kargs)

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
    logger = logging.getLogger(__name__)

    if (args.version):
        logger.info (f'{__iname__} {__version__}')
        sys.exit(0)

    command_map = parse_command_file(args.command_file)

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

                pre_scripts, post_scripts, script_file, script_args, script_vars = parse_command (command)

                if script_file is not None:

                    exec_local_commands(pre_scripts)

                    exec_remote_script (script_file,
                                        script_vars,
                                        no_command = args.no_command)
                    
                    exec_local_commands(pre_scripts)            

        except (EOFError, KeyboardInterrupt):
            # Exit the loop on Ctrl+D or Ctrl+C
            #logger.error("\nExiting...")
            break
        except Exception as e:
            # Print any errors that occur
            logger.error(f"Error: {e}")

    
    
