#!/usr/bin/env python3
"""
Reverso Anki - Python Version
A tool to process German words, translate them to English, and download pronunciations
for creating Anki flashcards.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
