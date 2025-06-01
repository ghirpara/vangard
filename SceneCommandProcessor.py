import json
import os
import sys
import shlex
import subprocess

from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory

from CommandMap import CommandMap
from CommandObject import CommandObject
from CommonUtils import common_logger, COLOR_COMMAND, COLOR_RESET, console, default_razor_config
from RazorConfig import RazorConfig

class SceneCommandProcessor:
    def __init__(self, command_file_name):
        self.razor_config = RazorConfig("razor.cfg", default_razor_config)
        self.command_map = CommandMap(command_file_name, self.razor_config)

        # --- Prompt entry history
        self.prompt_history_file = os.path.join(os.path.expanduser("~"), self.razor_config.get("razor_history_path", ".razor_history"))
        self.prompt_history = FileHistory(self.prompt_history_file)


        self.record_command_list=[]
        self.record_current=None

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

                #glogger.debug(f"Command map is {self.command_map.get_commands()}")

                for key in self.command_map.get_commands():
                    command   = self.command_map.get_command(key)
                    print(command.cli_line)

        else:

            try:
                command_object, script_args, script_vars = self.command_map.parse_command(key, parts[1:])
            except SystemExit as e:
                command_object=None
                script_args=None
                script_vars=None

        return command_object, script_args, script_vars


    def __init_command_record(self, command):
        self.record_current = command
        self.record_command_list = []

    def __load_command_record(self, filename):
        if (os.path.exists(filename)):
            content=json.load(open(filename, "r"))
            for command in content:
                self.__process_command(command)

    def __dump_command_record(self):
        if self.record_current is not None:
            record_file=open(self.record_current+".rec", "w")
            record_file.write(json.dumps(self.record_command_list))
            record_file.close()
            self.record_current = None

    def __exec_command(self, command_object, script_vars):
        command_object.exec_pre_command_scripts(script_vars)
        command_object.exec_remote_script(script_vars)
        command_object.exec_post_command_scripts(script_vars)

    def __process_command(self, command):
        command_object, script_args, script_vars = self.parse_command (command)

        common_logger.debug ("Command processed = " + command)
        common_logger.debug (f"   command obj    = {command_object}")
        common_logger.debug (f"   args           = {script_args}")
        common_logger.debug (f"   vars           = {script_vars}")

        if command_object is not None:

            if self.record_current is not None:
                self.record_command_list.append(command)

            self.__exec_command(command_object, script_vars)

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

                if len(command) > 0:

                    if command.startswith('!'):
                        parts=shlex.split(command[1:])
                        command=parts[0]
                        args=parts[1:]

                        if command =='q' or command == 'quit' or command == 'exit':
                            sys.exit(-1)
                        elif command == 'er' or command == 'end_record':
                            self.internal_command_end_record(self, args)
                        elif command == 'sr' or command == 'start_record':
                            self.internal_command_start_record(self, args)
                        elif command == 'lr' or command == 'load_record':
                            self.internal_command_load_record(self, args)
                        elif command == 'iv' or command == 'image-viewer':
                            self.internal_command_image_viewer(self, args)
            
                    else:

                        self.__process_command(command)

            except (EOFError, KeyboardInterrupt):
                # Exit the loop on Ctrl+D or Ctrl+C
                #glogger.error("\nExiting...")
                break
            except Exception as e:
                # Print any errors that occur
                common_logger.error(f"Error: {e}")
                continue

    
    def internal_command_end_record(self, args):
        self.__dump_command_record()

    def internal_command_start_record(self, args):
        self.__dump_command_record()
        self.__init_command_record(args[0])
        
    def internal_command_load_record(self, args):
        self.__load_command_record(args[0]+".rec")

    def internal_command_image_viewer(self, args):
        if len(args) > 1:
            ap=args[0]
        else:
            ap=None

        self.launch_image_viewer(pattern=ap)

    # --- Launching Logic ---
    def launch_image_viewer(self, pattern=None):
        """
        Launches the image viewer script as a separate process.
        """
        
        script_location = os.path.abspath(__file__)
        VIEWER_SCRIPT_PATH = f'{script_location}/../image_viewer.py'

        # Construct the command: [python_executable, script_path, --pattern, pattern_value]
        command = [sys.executable, VIEWER_SCRIPT_PATH]
        
        if pattern:
            pattern=pattern.replace("\"", "")
            pattern=pattern.replace("\'", "")
            command.extend(['--pattern', pattern])
        
        print(f"Launching image viewer with command: {' '.join(command)}")
        
        try:
            # Use Popen to run the command without blocking the current script
            # On Windows, creationflags=subprocess.DETACHED_PROCESS can sometimes help
            # to truly detach the process, but Popen alone is usually sufficient for GUIs.
            process = subprocess.Popen(command)
            print(f"Image viewer process started with PID: {process.pid}")
            return process
        except FileNotFoundError:
            print(f"Error: The script '{VIEWER_SCRIPT_PATH}' was not found.")
            print("Please ensure VIEWER_SCRIPT_PATH is correctly set.")
            return None
        except Exception as e:
            print(f"An error occurred while launching the viewer: {e}")
            return None