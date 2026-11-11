#!/usr/bin/env python3
"""
Nightclimb Arcade Launcher - Simple entry point
Run: python3 run.py
"""

import sys
import os

# Add package to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from launcher import cli_main

if __name__ == "__main__":
    cli_main()