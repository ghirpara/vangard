import os
import subprocess
import json
from abc import ABC, abstractmethod

from vangard.CommonUtils import common_logger, default_razor_config

class BaseCommand(ABC):
    """
    The abstract base class for all command handlers.
    """

    def __init__(self, name, app_state, cmd_config):
        """
        Initializes the command, giving it access to the application's shared state.

        :param app_state: A dictionary holding the application's state (e.g., database).
        """
        self.name         = name
        self.app_state    = app_state
        self.cmd_config   = cmd_config
        self.razor_config = default_razor_config

        common_logger.info(f"Initialize class {self.name} with app_state = {app_state}, cmd_config = {cmd_config}")

    def get_script(self, script_name):
        script_dirs = self.razor_config.get("alt_script_locations")
        for x in script_dirs:
            path=f"{x}/{script_name}"
            if os.path.exists(path):
                return os.path.abspath(path)
        return None

    def exec_default_script (self, args, daz_command_line:str|None):
        if "script-file" in self.cmd_config:
            script_path = self.get_script(self.cmd_config['script-file'])
            return self.exec_remote_script(script_path, args, daz_command_line)
        else:
            common_logger.warning(f"No default script found for command {self.name}.")
            

    def exec_remote_script (self, script_path, args, daz_command_line:str|None=None):    
        script_vars = vars(args)
        daz_root    = self.razor_config.get("daz_root")
        daz_args    = self.razor_config.get("daz_args")
        
        if (daz_args is None):
            daz_args = ""
        if (daz_command_line is None):
            daz_command_line = ""
        elif (isinstance(daz_command_line, list)):
            daz_command_line = " ".join(daz_command_line)

        if script_path is not None:
            mark_args="";
            if script_vars is not None:
                mark_args += f'{json.dumps(script_vars)}'

            command_expanded = f'"{daz_root}" -scriptArg \'{mark_args}\' {daz_args} {daz_command_line} {script_path}'

            common_logger.debug (f'Executing script file with command line: {command_expanded}') 

            process = subprocess.Popen (command_expanded, shell=False)

        else:
            common_logger.error(f"No valid script file was presented for command: {self.name}")
        

    @abstractmethod
    def process(self, args):
        """
        The main execution method for the command. This must be implemented by subclasses.

        :param args: The parsed arguments object from argparse.
        """

        common_logger.info(f"Calling BaseCommand.process; args={args}")

