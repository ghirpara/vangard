# Copyright (C) 2025 Blue Moon Foundary Software
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import argparse
import json
import shlex
import sys
import importlib
import os # To find a good path for history file

from .CommonUtils import common_logger

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import FuzzyCompleter, WordCompleter

class CommandProcessor:
    """
    A generic command processor that loads command definitions and handlers
    dynamically from a configuration file. Includes command history and autocompletion.
    """

    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.app_state = {
            'db': {},
            'next_id': 1
        }

        # --- Setup for prompt_toolkit ---
        self.history = FileHistory(os.path.expanduser('~/.app_history'))
        self.auto_suggest = AutoSuggestFromHistory()
        self.completer = self._create_completer()

        self.session = PromptSession(
            history=self.history,
            auto_suggest=self.auto_suggest,
            completer=self.completer,
            reserve_space_for_menu=4, # Give space for completion suggestions
        )
        # --- End of prompt_toolkit setup ---

        self.parser_cache={}
        self.command_cache={}

    def get_parser(self, command_name):
        if command_name in self.parser_cache:
            return self.parser_cache[command_name]

        parser = self._create_parser(command_name)
        if parser is not None:
            self.parser_cache[command_name] = parser

        return parser

    def get_command_instance(self, command_name):
        if command_name in self.command_cache:
            return self.command_cache[command_name]

        command_class = self._create_command_instance(command_name)
        if command_class is not None:
            self.command_cache[command_name]=command_class

        return command_class        

    def _create_completer(self):
        """
        Builds a completer object from the commands and arguments in the config.
        """
        completion_words = set(self.config.keys()) # Start with command names

        # Add all argument flags (e.g., '--all', '-p', '--priority')
        for command_config in self.config.values():
            for arg_config in command_config.get('arguments', []):
                completion_words.update(arg_config.get('names', []))
        
        # WordCompleter is simple and fast. FuzzyCompleter is more user-friendly.
        word_completer = WordCompleter(list(completion_words), ignore_case=True)
        return FuzzyCompleter(word_completer)

    def _load_config(self, config_path):
        # (This method is identical to the previous version)
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            common_logger.error(f"Error: Configuration file not found at '{config_path}'")
            sys.exit(1)
        except json.JSONDecodeError:
            common_logger.error(f"Error: Could not decode JSON from '{config_path}'")
            sys.exit(1)

    def _create_command_instance(self, command_name):
        # (This method is identical to the previous version)
        cmd_config = self.config.get(command_name, {})
        handler_path = cmd_config.get('handler_class')
        if not handler_path:
            common_logger.warning(f"Warning: No handler_class configured for command '{command_name}'.")
            return None
        try:
            module_path, class_name = handler_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            CmdClass = getattr(module, class_name)
            return CmdClass(class_name, self.app_state, cmd_config)
        except (ImportError, AttributeError) as e:
            common_logger.error(f"Error loading handler '{handler_path}': {e}")
            return None
        except Exception as e:
            common_logger.error(f"An unexpected error occurred while creating handler for '{command_name}': {e}")
            return None

    def _create_parser(self, command_name):
        # (This method is identical to the previous version)
        if command_name not in self.config:
            return None
        cmd_config = self.config[command_name]
        parser = argparse.ArgumentParser(
            prog=command_name,
            description=cmd_config.get('help', '')
        )
        type_mapping = {'str': str, 'int': int, 'float': float}
        for arg in cmd_config.get('arguments', []):
            names = arg.pop('names')
            if 'type' in arg and arg['type'] in type_mapping:
                arg['type'] = type_mapping[arg['type']]
            parser.add_argument(*names, **arg)
        return parser

    def _display_help(self):
        # (This method is identical to the previous version)
        common_logger.print("Available commands:")
        for command, config in self.config.items():
            common_logger.print(f"  {command:<15} {config.get('help', 'No description available.')}")
        common_logger.print("\nUse Up/Down arrows for history. Use Tab for autocompletion.")
        common_logger.print("Type 'help <command>' for more information on a specific command.")
        common_logger.print("Type 'exit' or 'quit' to close the application.")

    def run(self):
        """Starts the main loop to read and process commands."""
        common_logger.print("Welcome! Type 'help' for available commands or 'exit' to quit.")
        while True:
            try:
                # --- MODIFIED LINE: Use the prompt session instead of input() ---
                raw_input = self.session.prompt("> ")
                # --- END OF MODIFICATION ---

                if not raw_input:
                    continue

                tokens = shlex.split(raw_input)
                if not tokens: # Handle empty input after shlex split
                    continue
                command = tokens[0].lower()
                args = tokens[1:]

                if command in ['exit', 'quit']:
                    print("Exiting.")
                    break
                
                if command == 'help':
                    if args:
                        parser = self.get_parser(args[0])
                        if parser: parser.print_help()
                        else: common_logger.error(f"Error: Unknown command '{args[0]}'")
                    else:
                        self._display_help()
                    continue

                parser = self.get_parser(command)
                if not parser:
                    common_logger.error(f"Error: Unknown command '{command}'. Type 'help' for a list.")
                    continue

                try:
                    parsed_args = parser.parse_args(args)
                except SystemExit:
                    continue

                command_instance = self.get_command_instance(command)
                if command_instance:
                    command_instance.process(parsed_args)

            except (EOFError, KeyboardInterrupt):
                common_logger.error("\nExiting.")
                break

if __name__ == "__main__":
    processor = CommandProcessor('config.json')
    processor.run()
