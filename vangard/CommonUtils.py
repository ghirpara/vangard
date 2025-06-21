"""
    CommonUtils.py
 
   
 
    Author: G.Hirpara
    Version: 1.0.0
    Copyright (c) 2025 G.Hirpara
  
    LICENSING FOR THIS CODE IS DOCUMENTED IN THE ACCOMPANYING LICENSE.md FILE. 
    USERS OF THIS CODE AGREE TO TERMS AND CONDITIONS OUTLINED IN THE LICENSE.
  
"""

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

default_razor_config = {
    "daz_root": "c:/Program Files/DAZ 3D/DAZStudio4/DAZStudio.exe",
    "daz_args": "",
    "alt_script_locations": ["./dazscripts"]
}
