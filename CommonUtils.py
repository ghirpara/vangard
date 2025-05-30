import os
import sys
import logging
from logging import FileHandler
from rich.logging import RichHandler
from textual.app import App, ComposeResult
from textual.widget import Widget
from textual.widgets import Button, Label, RichLog

from pathlib import Path
from typing import Any
from rich.console import Console # Import rich Console
from rich.markdown import Markdown # Import rich Markdown renderer

from prompt_toolkit.completion import NestedCompleter


logging.basicConfig()

class LoggingConsole(RichLog):
    file = False
    console: Widget

    def print(self, content):
        self.write(content)


common_logger = logging.getLogger(__name__)
rich_log_handler = RichHandler(console=LoggingConsole(), rich_tracebacks=True)
file_handler     = FileHandler("razor.log")

common_logger.addHandler(rich_log_handler)
common_logger.addHandler(file_handler)


script_location = Path(__file__).resolve().parent     
console=Console()        

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

default_razor_config = {
    "daz_root": "c:/Program Files/DAZ 3D/DAZStudio4/DAZStudio.exe",
    "alt_script_locations": []
}