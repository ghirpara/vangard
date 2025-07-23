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


import sys
import logging
from logging import FileHandler
from rich.logging import RichHandler
from textual.widget import Widget
from textual.widgets import RichLog
from colorama import Fore, Back, Style

from pathlib import Path
from rich.console import Console # Import rich Console

from prompt_toolkit.completion import NestedCompleter

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
 


logging.basicConfig()

class LoggingConsole(RichLog):
    file = False
    console: Widget

    def print(self, content):
        self.write(content)

class CommonLogger:
    def __init__(self):

        self.common_logger = logging.getLogger(__name__)
        self.rich_log_handler = RichHandler(console=LoggingConsole(), rich_tracebacks=True)
        self.file_handler     = FileHandler("razor.log")

        self.common_logger.addHandler(self.rich_log_handler)
        self.common_logger.addHandler(self.file_handler)


    def print(self, message):
        print (f"{Fore.BLUE}{message}{COLOR_RESET}")
        
    def info(self, message):
        self.common_logger.info(f"{Fore.BLUE}{message}{COLOR_RESET}")

    def warning(self, message):
        self.common_logger.info(f"{Fore.YELLOW}{message}{COLOR_RESET}")

    def error(self, message):
        self.common_logger.info(f"{Fore.RED}{message}{COLOR_RESET}")

    def debug(self, message):
        self.common_logger.info(f"{Fore.GREEN}{message}{COLOR_RESET}")

    def setLevel(self, level):
        self.common_logger.setLevel(level)


common_logger = CommonLogger()

script_location = Path(__file__).resolve().parent     
daz_script_location = Path(f"{__file__}/..").resolve()
console=Console()        



type_dict = {
    'int': int,
    'float': float,
    'str': str,
    'list': list,
    'dict': dict,
    'bool': bool
}    

#    "daz_root": "c:/Program Files/DAZ 3D/DAZStudio4/DAZStudio.exe",

default_razor_config = {
    "daz_root": "x:/DAZNext/Applications/64-bit/DAZ 3D/DAZStudio4/DAZStudio.exe",
    "daz_args": "",
    "alt_script_locations": ["./dazscripts"]
}
