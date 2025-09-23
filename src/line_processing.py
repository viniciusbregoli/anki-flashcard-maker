"""
Line processing module for translating words and creating Anki cards.
"""

import os
import time
import glob
from typing import List, Dict, Any
from openai_api import OpenAIAPI
from download_audio import download_pronunciation
from utils.utils import capitalize_string, sanitize_filename, detect_input_type


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

    def __init__(
        self,
        card_id: int,
        source: str,
        translation: List[str],
        context: List[Dict[str, str]],
        gender: str = "",
        plural: str = "",
        input_type: str = "word",
    ):
        self.id = card_id
        self.source = source
        self.translation = translation
        self.context = context
        self.gender = gender
        self.plural = plural
        self.input_type = input_type  # 'word', 'expression', or 'sentence'


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
    """Processes a single input (word, expression, or sentence) using the OpenAI API and creates a Card."""
    try:
        # Detect input type
        input_type = detect_input_type(line)
        print(f"  Detected type: {input_type}")

        # Get details based on input type
        if input_type == "word":
            details = await openai_api.get_word_details(line.lower())
        elif input_type == "expression":
            details = await openai_api.get_expression_details(line)
        else:  # sentence
            details = await openai_api.get_sentence_details(line)

        if "N/A" in details["translation"]:
            print(f"  - OpenAI failed to process '{line}'. Skipping.")
            return None

        # Download pronunciation only for single words
        if input_type == "word":
            await download_pronunciation(line, "de", index)
        else:
            print(f"  - Skipping audio download for {input_type}")

        # Create card
        return Card(
            card_id=index,
            source=capitalize_string(line) if input_type == "word" else line,
            translation=details.get("translation", []),
            context=details.get("context", []),
            gender=details.get("gender", ""),
            plural=details.get("plural", "") if input_type == "word" else "",
            input_type=input_type,
        )
    except Exception as e:
        print(f"An error occurred while processing the line '{line}': {e}")
        return None


def write_cards_to_file(cards: List[Card], output_file_path: str):
    """Write all cards to the output file in Anki format, with a semicolon separating the front and back fields."""
    try:
        with open(output_file_path, "w", encoding="utf-8") as file:
            for card in cards:
                # Prepare translation
                translation = ", ".join(card.translation)

                if card.input_type == "word":
                    # Word format: [sound] (gender) word (plural) + context
                    gender_display = (
                        f"({card.gender}) "
                        if card.gender and card.gender != "N/A"
                        else ""
                    )
                    plural_display = (
                        f" (pl: {card.plural})"
                        if card.plural and card.plural != "N/A"
                        else ""
                    )
                    sound_field = (
                        f"[sound:{sanitize_filename(card.source)}_pronunciation.mp3]"
                    )

                    front_parts = [
                        f"{sound_field} {gender_display}{card.source}{plural_display}"
                    ]
                    back_parts = [translation]

                    if card.context and card.context[0].get("german") != "N/A":
                        context_german = card.context[0]["german"]
                        context_english = card.context[0]["english"]
                        front_parts.append(f"<i>{context_german}</i>")
                        back_parts.append(f"<i>{context_english}</i>")

                elif card.input_type == "expression":
                    # Expression format: expression + context (no audio, no gender)
                    front_parts = [card.source]
                    back_parts = [translation]

                    if card.context and card.context[0].get("german") != "N/A":
                        context_german = card.context[0]["german"]
                        context_english = card.context[0]["english"]
                        front_parts.append(f"<i>{context_german}</i>")
                        back_parts.append(f"<i>{context_english}</i>")

                else:  # sentence
                    # Sentence format: just sentence -> translation (no context, no audio, no gender)
                    front_parts = [card.source]
                    back_parts = [translation]

                front_field = "<br>".join(front_parts)
                back_field = "<br>".join(back_parts)

                # Write to file with a semicolon separator
                file.write(f"{front_field};{back_field}\n")

        print(f"Cards written to: {output_file_path}")
    except Exception as error:
        print(f"Error writing to output file: {error}")
        raise
