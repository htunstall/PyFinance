"""
Main module for PyFinance. When executed it will bring up the gui to navigate
the software.
"""

__version__ = "1.0.1"
__author__  = "Harry Tunstall"

import gui
import lookup
import database


licence = "PyFinance  Copyright (C) 2022  {}\n\n".format(__author__) + \
          "This program comes with ABSOLUTELY NO WARRANTY\n" + \
          "This is free software, and you are welcome to redistribute it\n" + \
          "under certain conditions."

about   = "Version: {}\n\n{}".format(__version__, licence)
       
if __name__ == "__main__":
    gui.openApp(about)