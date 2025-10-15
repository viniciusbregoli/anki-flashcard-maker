#!/usr/bin/env python3
"""
DeepL Anki - Python Version
A tool to process German words, translate them to English, and download pronunciations
for creating Anki flashcards.
"""

import sys
import asyncio
import os
import shutil
from dotenv import load_dotenv
from line_processing import process_lines
from utils import read_input_file


def prepare_for_anki():
    """Copy audio files to Anki media folder."""
    
    # Anki media folder path
    anki_media_path = "/home/bregoli/.local/share/Anki2/User 1/collection.media"
    
    # Check if Anki media folder exists
    if not os.path.exists(anki_media_path):
        print(f"✗ Anki media folder not found: {anki_media_path}")
        print("Please check your Anki installation path.")
        return
    
    # Copy audio files to Anki media folder
    audio_dir = "audio"
    if os.path.exists(audio_dir):
        audio_files = [f for f in os.listdir(audio_dir) if f.endswith('.mp3')]
        if audio_files:
            for audio_file in audio_files:
                src = os.path.join(audio_dir, audio_file)
                dst = os.path.join(anki_media_path, audio_file)
                shutil.copy2(src, dst)
                print(f"✓ Copied {audio_file} to Anki media folder")
        else:
            print("No audio files found.")
    else:
        print("No audio directory found.")
    
    print(f"\n🎉 Audio files copied to Anki media folder!")
    print(f"📁 Anki media folder: {anki_media_path}")
    print(f"🎵 Audio files: {len(audio_files) if 'audio_files' in locals() else 0} files")
    
    print(f"\n📋 Anki Import Instructions:")
    print(f"1. Open Anki")
    print(f"2. Go to File > Import")
    print(f"3. Select: {os.path.abspath('output.txt')}")
    print(f"4. Set Field separator to: Semicolon")
    print(f"5. Click Import")
    print(f"6. Audio files are already in your Anki media folder!")


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
        
        # Prepare for Anki import
        print("\n" + "="*50)
        print("PREPARING FOR ANKI IMPORT...")
        print("="*50)
        prepare_for_anki()

    except Exception as error:
        print(f"Error processing cards: {error}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
