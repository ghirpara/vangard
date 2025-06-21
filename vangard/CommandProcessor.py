import argparse
import json
import shlex
import sys
import importlib
from .CommonUtils import common_logger

class CommandProcessor:
    """
    A generic command processor that loads command definitions and handlers
    dynamically from a configuration file.
    """

    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        # Application state is managed here, not with globals
        self.app_state = {
            'db': {},
            'next_id': 1
        }
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
        

    def _load_config(self, config_path):
        """Loads the command configuration from a JSON file."""
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
        """
        Dynamically imports and instantiates a command handler class.
        """
        cmd_config = self.config.get(command_name, {})
        handler_path = cmd_config.get('handler_class')

        if not handler_path:
            common_logger.warning(f"Warning: No handler_class configured for command '{command_name}'.")
            return None

        try:
            # Split the path into module and class name (e.g., 'commands.add.AddTaskCommand')
            module_path, class_name = handler_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            CmdClass = getattr(module, class_name)
            # Instantiate the command, passing the application state
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
        common_logger.info("Available commands:")
        for command, config in self.config.items():
            common_logger.info(f"  {command:<15} {config.get('help', 'No description available.')}")
        common_logger.info("\nType 'help <command>' for more information on a specific command.")
        common_logger.info("Type 'exit' or 'quit' to close the application.")

    def run(self):
        """Starts the main loop to read and process commands."""
        common_logger.info("Welcome! Type 'help' for available commands or 'exit' to quit.")
        while True:
            try:
                raw_input = input("> ")
                if not raw_input:
                    continue

                tokens = shlex.split(raw_input)
                command = tokens[0].lower()
                args = tokens[1:]

                if command in ['exit', 'quit']:
                    common_logger.info("Exiting.")
                    break
                
                if command == 'help':
                    if args:
                        parser = self.get_parser(args[0])
                        #parser = self._create_parser(args[0])
                        if parser: parser.print_help()
                        else: common_logger.error(f"Error: Unknown command '{args[0]}'")
                    else:
                        self._display_help()
                    continue

                #parser = self._create_parser(command)
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
                    # Execute the command's process method
                    command_instance.process(parsed_args)

            except (EOFError, KeyboardInterrupt):
                common_logger.error("\nExiting.")
                break

if __name__ == "__main__":
    processor = CommandProcessor('config.json')
    processor.run()
    
