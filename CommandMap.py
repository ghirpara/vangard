import json
from pathlib import Path
from CommandObject import CommandObject
from CommonUtils import common_logger

class CommandMap:

    def __init__(self, command_file_name, config):

        self.config = config
        self.commands = {}

        command_file_object=json.load(open(command_file_name, 'r'))

        script_dir = Path(__file__).resolve().parent

        self.script_locations = [
            f"{script_dir}/dazscripts"
        ]

        for alt in self.config.get("alt_script_locations", []):
            self.script_locations.append(alt)

        for key in command_file_object:
            command = command_file_object[key]
            self.commands[key]= CommandObject(self, key, command)

    def parse_command(self, key, command_line):
        command = self.commands.get(key, None)
        script_args = None
        script_vars = None

        if command is not None:
            try:
                common_logger.debug(f"Parsing command line for key {key} as {command_line}")
                script_args = command.parser.parse_args(command_line)
                script_vars = vars(script_args)
            except Exception as e:
                common_logger.error(f"Failed to locate command for {key}: {str(e)}")
                script_args = None
                script_vars = None
        else:
            common_logger.ingo(f"Could not identify command from command: key={key}, cli={command_line}")

        return command, script_args, script_vars

    def get_commands(self):
        return self.commands

    def get_command(self, key):
        return self.commands.get(key, None)