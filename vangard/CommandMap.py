"""
    CommandMap.py
 
   
 
    Author: G.Hirpara
    Version: 1.0.0
    Copyright (c) 2025 G.Hirpara
  
    LICENSING FOR THIS CODE IS DOCUMENTED IN THE ACCOMPANYING LICENSE.md FILE. 
    USERS OF THIS CODE AGREE TO TERMS AND CONDITIONS OUTLINED IN THE LICENSE.
  

"""



import json
from pathlib import Path
from .CommandObject import CommandObject
from .CommonUtils import common_logger

class CommandMap:

    def __init__(self, command_file_name, config):

        self.config = config
        self.commands = {}

        command_file_object=json.load(open(command_file_name, 'r'))

        script_dir = Path(__file__).resolve().parent

        self.script_locations = [
            f"{script_dir}/../dazscripts"
        ]

        for alt in self.config.get("alt_script_locations", []):
            self.script_locations.append(alt)

        for key in command_file_object:
            common_logger.debug(f"Generating command object {key}")
            command = command_file_object[key]
            self.commands[key]= CommandObject(self, key, command)

    def parse_command(self, key, command_line):
        command = self.commands.get(key, None)
        script_args = None
        script_vars = None
        daz_command_line = None

        # Any elements of the command_line that occur after the string "--" should be parsed seperately 
    
        common_logger.debug(f"Pre-Parsing command line for key {key} as {command_line}")            

        if command is not None:
            try:
                if '--' in command_line:
                    sc_command_line  = command_line[:command_line.index("--")]
                    daz_command_line = command_line[command_line.index("--")+1:]
                else:
                    sc_command_line  = command_line

                common_logger.debug(f"Parsing command line for key {key} as {sc_command_line}")
                script_args = command.parser.parse_args(sc_command_line)
                script_vars = vars(script_args)
            except Exception as e:
                common_logger.error(f"Failed to locate command for {key}: {str(e)}")
                script_args = None
                script_vars = None
        else:
            common_logger.ingo(f"Could not identify command from command: key={key}, cli={command_line}")

        return command, script_args, script_vars, daz_command_line

    def get_commands(self):
        return self.commands

    def get_command(self, key):
        return self.commands.get(key, None)