import argparse
import json
import shlex
import sys
import importlib

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

    def _load_config(self, config_path):
        """Loads the command configuration from a JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file not found at '{config_path}'")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from '{config_path}'")
            sys.exit(1)

    def _get_command_instance(self, command_name):
        """
        Dynamically imports and instantiates a command handler class.
        """
        cmd_config = self.config.get(command_name, {})
        handler_path = cmd_config.get('handler_class')

        if not handler_path:
            print(f"Warning: No handler_class configured for command '{command_name}'.")
            return None

        try:
            # Split the path into module and class name (e.g., 'commands.add.AddTaskCommand')
            module_path, class_name = handler_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            CmdClass = getattr(module, class_name)
            # Instantiate the command, passing the application state
            return CmdClass(self.app_state)
        except (ImportError, AttributeError) as e:
            print(f"Error loading handler '{handler_path}': {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while creating handler for '{command_name}': {e}")
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
        print("Available commands:")
        for command, config in self.config.items():
            print(f"  {command:<15} {config.get('help', 'No description available.')}")
        print("\nType 'help <command>' for more information on a specific command.")
        print("Type 'exit' or 'quit' to close the application.")

    def run(self):
        """Starts the main loop to read and process commands."""
        print("Welcome! Type 'help' for available commands or 'exit' to quit.")
        while True:
            try:
                raw_input = input("> ")
                if not raw_input:
                    continue

                tokens = shlex.split(raw_input)
                command = tokens[0].lower()
                args = tokens[1:]

                if command in ['exit', 'quit']:
                    print("Exiting.")
                    break
                
                if command == 'help':
                    if args:
                        parser = self._create_parser(args[0])
                        if parser: parser.print_help()
                        else: print(f"Error: Unknown command '{args[0]}'")
                    else:
                        self._display_help()
                    continue

                parser = self._create_parser(command)
                if not parser:
                    print(f"Error: Unknown command '{command}'. Type 'help' for a list.")
                    continue

                try:
                    parsed_args = parser.parse_args(args)
                except SystemExit:
                    continue

                command_instance = self._get_command_instance(command)
                if command_instance:
                    # Execute the command's process method
                    command_instance.process(parsed_args)

            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break

if __name__ == "__main__":
    processor = CommandProcessor('config.json')
    processor.run()