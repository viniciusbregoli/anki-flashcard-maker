#!/usr/bin/env python3
"""
DeepL Anki - Python Version
A tool to process German words, translate them to English, and download pronunciations
for creating Anki flashcards.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from line_processing import process_lines
from utils.utils import read_input_file

async def main():
    """Main function to orchestrate the word processing workflow."""
    try:
        # Load environment variables from .env file
        load_dotenv()
        
        # Read the input file
        input_file_path = "input.txt"
        lines_array = read_input_file(input_file_path)
        
        if not lines_array:
            print("No words found in input file or file is empty.")
            return
        
        print(f"Found {len(lines_array)} words to process:")
        for i, word in enumerate(lines_array, 1):
            print(f"{i:3d}. {word}")
        print()
        
        # Process each line
        await process_lines(lines_array)
        
        print("\nProcessing completed successfully!")
        print("Check 'output.txt' for the results.")
        
    except Exception as error:
        print(f"Error processing cards: {error}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
