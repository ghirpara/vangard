
import os
import sys
import json
import argparse
import logging
import subprocess
import shlex
from pathlib import Path
from typing import Any
from rich.console import Console # Import rich Console
from rich.markdown import Markdown # Import rich Markdown renderer

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory # Optional: For persistent history
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory # Optional: Suggest based on history
from prompt_toolkit.completion import NestedCompleter

from razor_config import RazorConfig
from command_map import CommandMap, CommandObject
import user_functions

script_location = Path(__file__).resolve().parent     
console=Console()        

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
 

default_razor_config = {
    "daz_root": "c:/Program Files/DAZ 3D/DAZStudio4/DAZStudio.exe",
    "alt_script_locations": []
}

class SceneCommandProcessor:
    def __init__(self, command_file_name):
        self.razor_config = RazorConfig("razor.cfg", default_razor_config)
        self.command_map = CommandMap(command_file_name, self.razor_config)

        # --- Prompt entry history
        self.prompt_history_file = os.path.join(os.path.expanduser("~"), self.razor_config.get("razor_history_path", ".razor_history"))
        self.prompt_history = FileHistory(self.prompt_history_file)

    def parse_command(self, command:str) -> tuple[None|CommandObject, dict, list]:

        command_object=None
        script_args=None
        script_vars=None

        parts = shlex.split(command)

        key = parts[0]

        if key == 'help':

            lines=[]
            if len(parts) > 1:

                key = parts[1]
                
                command = self.command_map.get_command(key)

                if command is None:
                    lines.append(f'Unknown command specified: {COLOR_COMMAND}{key}{COLOR_RESET}')
                
                else:
                    print(command.cli_line)
                    print(command.help_str)

            else:

                #logging.debug(f"Command map is {self.command_map.get_commands()}")
    
                for key in self.command_map.get_commands():
                    command   = self.command_map.get_command(key)
                    print(command.cli_line)

        else:

            command_object, script_args, script_vars = self.command_map.parse_command(key, parts[1:])

        return command_object, script_args, script_vars

    def process_loop(self):
        console.print("Welcome to the Daz Scene Commander CLI")
        console.print ("   'exit' to quit)")

        while True:
            try:
                # Read input from the user
                command = prompt(
                    ">",
                    history=self.prompt_history,                   # Enable history
                    auto_suggest=AutoSuggestFromHistory(), # Enable suggestions
                )   

                command = command.strip()

                if len(command.strip()) > 0:

                    command_object, script_args, script_vars = self.parse_command (command)

                    logging.debug ("Command processed = " + command)
                    logging.debug (f"   command obj    = {command_object}")
                    logging.debug (f"   args           = {script_args}")
                    logging.debug (f"   vars           = {script_vars}")

                    if command_object is not None:
                        command_object.exec_pre_command_scripts()
                        command_object.exec_remote_script(script_vars)
                        command_object.exec_post_command_scripts()

            except (EOFError, KeyboardInterrupt):
                # Exit the loop on Ctrl+D or Ctrl+C
                #logger.error("\nExiting...")
                break
            except Exception as e:
                # Print any errors that occur
                logging.error(f"Error: {e}")