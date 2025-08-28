"""
Line processing module for translating words and creating Anki cards.
"""

import os
import time
import glob
from typing import List, Dict, Any
from openai_api import OpenAIAPI
from download_audio import download_pronunciation
from utils.utils import capitalize_string, sanitize_filename

def cleanup_previous_audio():
    """Delete all previously downloaded audio files."""
    try:
        audio_dir = "audio"
        if os.path.exists(audio_dir):
            mp3_files = glob.glob(os.path.join(audio_dir, "*.mp3"))
            if mp3_files:
                print(f"Cleaning up {len(mp3_files)} previous audio files...")
                for f in mp3_files:
                    os.remove(f)
                print("Audio cleanup completed.")
    except Exception as error:
        print(f"Warning: Error during audio cleanup: {error}")

class Card:
    """Represents an Anki flashcard."""
    def __init__(self, card_id: int, source: str, translation: List[str], context: List[Dict[str, str]], gender: str = ""):
        self.id = card_id
        self.source = source
        self.translation = translation
        self.context = context
        self.gender = gender

async def process_lines(lines_array: List[str]):
    """Process each line from the input file to create Anki cards."""
    cleanup_previous_audio()
    cards = []
    openai_api = OpenAIAPI()
    output_file_path = "output.txt"
    
    print("Starting to process words with OpenAI...")
    for i, line in enumerate(lines_array):
        print(f"Processing word {i+1}/{len(lines_array)}: {line}")
        card = await process_line(line, i, openai_api)
        if card:
            cards.append(card)
            print(f"✓ Successfully processed: {line}")
        else:
            print(f"✗ Failed to process: {line}")
        time.sleep(1)  # Small delay to avoid overwhelming APIs
    
    write_cards_to_file(cards, output_file_path)
    print(f"\nProcessed {len(cards)} cards successfully.")

async def process_line(line: str, index: int, openai_api: OpenAIAPI) -> Card:
    """Processes a single word using the OpenAI API and creates a Card."""
    try:
        word_details = await openai_api.get_word_details(line.lower())
        
        if "N/A" in word_details['translation']:
             print(f"  - OpenAI failed to process '{line}'. Skipping.")
             return None

        # Download pronunciation
        await download_pronunciation(line, "de", index)
        
        # Create card
        return Card(
            card_id=index,
            source=capitalize_string(line),
            translation=word_details.get('translation', []),
            context=word_details.get('context', []),
            gender=word_details.get('gender', '')
        )
    except Exception as e:
        print(f"An error occurred while processing the line '{line}': {e}")
        return None

def write_cards_to_file(cards: List[Card], output_file_path: str):
    """Write all cards to the output file in Anki format."""
    try:
        with open(output_file_path, 'w', encoding='utf-8') as file:
            for card in cards:
                gender_display = f" ({card.gender})" if card.gender and card.gender != "N/A" else ""
                
                if card.context and card.context[0].get('german') != "N/A":
                    context_german = card.context[0]['german']
                    context_english = card.context[0]['english']
                    line = (
                        f"[sound:{sanitize_filename(card.source)}_pronunciation.mp3] "
                        f"{card.source}{gender_display} <br> "
                        f"{', '.join(card.translation)} <br> "
                        f"<i>{context_german}</i> <br> "
                        f"<i>{context_english}</i>\n"
                    )
                else:
                    line = (
                        f"[sound:{sanitize_filename(card.source)}_pronunciation.mp3] "
                        f"{card.source}{gender_display} <br> "
                        f"{', '.join(card.translation)}\n"
                    )
                file.write(line)
        print(f"Cards written to: {output_file_path}")
    except Exception as error:
        print(f"Error writing to output file: {error}")
        raise
