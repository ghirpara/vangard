"""
    CommandObject.py
 
   
 
    Author: G.Hirpara
    Version: 1.0.0
    Copyright (c) 2025 G.Hirpara
  
    LICENSING FOR THIS CODE IS DOCUMENTED IN THE ACCOMPANYING LICENSE.md FILE. 
    USERS OF THIS CODE AGREE TO TERMS AND CONDITIONS OUTLINED IN THE LICENSE.
  
"""

import argparse
import json
import os
import shlex
import subprocess

import vangard

from .CommonUtils import common_logger, type_dict, COLOR_RESET, COLOR_ARGS, COLOR_COMMAND
from .UserFunctions import *

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

        if ('script-file' in command):
      
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
                'script-location': self.script_location
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
                common_logger.info (f"Added script {test}")
                break
            else:
                common_logger.error (f"Could not locate script {test}. Make sure path exists and is readable.")

    def get_script_mapping(self, script_name):
        return self.script_map.get(script_name, None)

    def exec_pre_command_scripts(self, script_vars):
        if self.pre_scripts is not None:
            self.exec_local_commands(self.pre_scripts, script_vars)

    def exec_post_command_scripts(self, script_vars):
        if self.post_scripts is not None:
            self.exec_local_commands(self.post_scripts, script_vars)

    def exec_local_commands(self, scripts, script_vars):

        common_logger.debug(f"SCRIPTS = {scripts}")

        if scripts is not None:
            for script in scripts:
                kargs={}
                script_args = script["script-args"]
                for arg in script_args:
                    kargs[arg]=script_vars[arg]
                    callback=getattr(vangard.UserFunctions, script["script-callback"])
                    rv=callback(**kargs)
                    if arg in rv:
                        print (f"#### TEST RV={rv}")
                        script_vars[arg]=rv[arg]


    def exec_remote_script (self, script_vars:dict, daz_command_line:str|None):
        daz_root = self.container.config.get("daz_root")
        daz_args = self.container.config.get("daz_args")

        if (daz_args is None):
            daz_args = ""
        if (daz_command_line is None):
            daz_command_line = ""
        elif (isinstance(daz_command_line, list)):
            daz_command_line = " ".join(daz_command_line)

        if self.script_location is not None:
            mark_args="";
            if script_vars is not None:
                mark_args += f'{json.dumps(script_vars)}'

            command_expanded = f'"{daz_root}" -scriptArg \'{mark_args}\' {daz_args} {daz_command_line} {self.script_location}'

            common_logger.debug (f'Executing script file with command line: {command_expanded}') 

            process = subprocess.Popen (command_expanded, shell=False)

        else:
            common_logger.error(f"No valid script file was presented for command: {self.key}")
