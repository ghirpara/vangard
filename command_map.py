import os
import sys
import json
import subprocess
import argparse
import shlex
from pathlib import Path
import user_functions
from glogger import glogger

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
 

type_dict = {
    'int': int,
    'float': float,
    'str': str,
    'list': list,
    'dict': dict,
    'bool': bool
}    

class CommandObject:
    def __init__(self, container, key, command:dict):

        self.key           = key
        self.container     = container
        self.command_entry = command
             
        # Extract pre and post script actions
        self.pre_scripts = command.get('pre-scripts')
        self.post_scripts = command.get('post-scripts')

        # Locate the actual location of the script file 
        self.script_location = None
        self.__add_script_mapping(command['script-file'])

        # Create the parser object for the command
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
        self.parser=parser    

        self.__add_help_and_usage()

    def __str__(self):
            data = {
                'command': self.key,
                'pre-scripts': self.pre_scripts,
                'post-scripts': self.post_scripts,
                'script-loction': self.script_location
            }
            return f"{data}"

    def __repr__(self):
        return self.__str__()

    def __add_help_and_usage(self):
        usage_str=self.parser.format_usage()
        parts=shlex.split(usage_str)
        self.cli_line = f"{COLOR_COMMAND}{parts[1]} {COLOR_RESET}{COLOR_ARGS}{' '.join(parts[2:])}{COLOR_RESET}"
        self.help_str = self.parser.format_help()


    def __add_script_mapping(self, script_name):
        for key in self.container.script_locations:
            test = f"{key}/{script_name}"
            if (os.path.exists(test)):
                self.script_location = test
                glogger.info (f"Added script {test}")
                break
            else:
                glogger.error (f"Could not locate script {test}. Make sure path exists and is readable.")

    def get_script_mapping(self, script_name):
        return self.script_map.get(script_name, None)

    def exec_pre_command_scripts(self, script_vars):
        if self.pre_scripts is not None:
            self.exec_local_commands(self.pre_scripts, script_vars)

    def exec_post_command_scripts(self, script_vars):
        if self.post_scripts is not None:
            self.exec_local_commands(self.post_scripts, script_vars)

    def exec_local_commands(self, scripts, script_vars):

        glogger.debug(f"SCRIPTS = {scripts}")

        if scripts is not None:
            for script in scripts:                      
                kargs={}
                script_args = script["script-args"]
                for arg in script_args:
                    kargs[arg]=script_vars[arg]
                    callback=getattr(user_functions, script["script-callback"])
                    callback(**kargs)

    
    def exec_remote_script (self, script_vars:dict):
        daz_root = self.container.config.get("daz_root")

        if self.script_location is not None:        
            mark_args="";        
            if script_vars is not None:
                mark_args += f'{json.dumps(script_vars)}'

            glogger.debug (f'Executing script file: root={daz_root} {self.script_location} MA={mark_args}')
            process = subprocess.Popen (f'"{daz_root}" -scriptArg \'{mark_args}\' {self.script_location}',
                                        shell=False)
        else:
            glogger.error(f"No valid script file was presented for command: {self.key}")
   

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
                glogger.debug(f"Parsing command line for key {key} as {command_line}")
                script_args = command.parser.parse_args(command_line)
                script_vars = vars(script_args)
            except Exception as e:
                glogger.error(f"Failed to locate command for {key}: {str(e)}")
                script_args = None
                script_vars = None
        else:
            glogger.ingo(f"Could not identify command from command: key={key}, cli={command_line}")

        return command, script_args, script_vars

    def get_commands(self):
        return self.commands
    
    def get_command(self, key):
        return self.commands.get(key, None)