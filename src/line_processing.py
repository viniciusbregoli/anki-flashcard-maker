"""
Line processing module for translating words and creating Anki cards.
"""

import os
import time
import glob
from typing import List, Dict, Any
from openai_api import OpenAIAPI
from download_audio import download_pronunciation
from utils import capitalize_string, sanitize_filename, detect_input_type


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
        tip: str = "",
        audio_source: str = None
    ):
        self.id = card_id
        self.source = source
        self.translation = translation
        self.context = context
        self.gender = gender
        self.plural = plural
        self.input_type = input_type
        self.tip = tip
        
        # Audio filename is derived from the successfully downloaded text (audio_source)
        # If no audio_source was provided (meaning download failed or wasn't attempted), we explicitly set None
        if audio_source:
             self.audio_filename = f"{sanitize_filename(audio_source.lower())}_pronunciation.mp3"
        else:
             self.audio_filename = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert card to dictionary for API response."""
        return {
            "id": self.id,
            "source": self.source,
            "translation": self.translation,
            "context": self.context,
            "gender": self.gender,
            "plural": self.plural,
            "input_type": self.input_type,
            "tip": self.tip,
            "audio": self.audio_filename
        }


async def generate_cards(lines_array: List[str], openai_api: OpenAIAPI = None, progress_callback=None) -> List[Card]:
    """
    Process words and return a list of Card objects.
    Does not write to file.
    """
    if openai_api is None:
        openai_api = OpenAIAPI()

    cards = []
    print("Starting to process words with OpenAI...")
    total_lines = len(lines_array)
    for i, line in enumerate(lines_array):
        # Notify progress if callback exists
        if progress_callback:
            await progress_callback(i, total_lines, line)

        print(f"Processing word {i+1}/{total_lines}: {line}")
        card = await process_line(line, i, openai_api)
        if card:
            cards.append(card)
            print(f"✓ Successfully processed: {line}")
        else:
            print(f"✗ Failed to process: {line}")
        time.sleep(1)  # Small delay to avoid overwhelming APIs
    
    return cards


async def process_lines(lines_array: List[str]):
    """Process each line from the input file to create Anki cards."""
    cleanup_previous_audio()
    
    # Generate the cards
    cards = await generate_cards(lines_array)

    output_file_path = "output.txt"
    write_cards_to_file(cards, output_file_path)
    print(f"\nProcessed {len(cards)} cards successfully.")


async def process_line(line: str, index: int, openai_api: OpenAIAPI) -> Card:
    try:
        # Use AI to detect type and get details
        details = await openai_api.analyze_german_content(line)
        input_type = details.get("type", "word")
        print(f"  Detected type: {input_type}")

        if "N/A" in details["translation"]:
            print(f"  - OpenAI failed to process '{line}'. Skipping.")
            return None

        source_text = line
        tip = details.get("tip", "")

        if input_type == "word":
            source_text = capitalize_string(line)
            gender = details.get("gender", "")
            
            # 1. Redundancy Removal
            # Check if source_text starts with the gender (case-insensitive)
            # e.g. "Der Schreibtisch" starts with "der ".lower()
            if gender and source_text.lower().startswith(f"{gender.lower()} "):
                # Remove the article and the space
                source_text = source_text[len(gender) + 1:].strip()
                # Ensure the new source text is capitalized
                source_text = capitalize_string(source_text)
            
            # 2. Audio Strategy
            audio_text_success = None
            
            # Try with gender first (e.g. "der Tisch")
            if gender and gender not in ["N/A", ""]:
                audio_query = f"{gender} {source_text}"
                success = await download_pronunciation(audio_query, "de", index)
                if success:
                    audio_text_success = audio_query
                else:
                    print(f"  - Audio for '{audio_query}' failed. Trying '{source_text}'...")
            
            # Fallback to just the word if gender failed or didn't exist
            if not audio_text_success:
                audio_query = source_text
                success = await download_pronunciation(audio_query, "de", index)
                if success:
                    audio_text_success = audio_query
                else:
                    print(f"  - Forvo audio for '{audio_query}' also failed. Trying OpenAI TTS...")
                    # Fallback to OpenAI TTS
                    filename = f"{sanitize_filename(audio_query.lower())}_pronunciation.mp3"
                    filepath = os.path.join("audio", filename)
                    tts_success = await openai_api.generate_speech(audio_query, filepath)
                    if tts_success:
                        audio_text_success = audio_query # We use the query as source, filename logic handles path
                    else:
                        print(f"  - OpenAI TTS failed for '{audio_query}'.")
            
        else:
            # Expressions and Sentences always use OpenAI TTS
            print(f"  - Generating OpenAI TTS for {input_type}...")
            # Use the full line as source
            audio_query = line.strip()
            # If it's too long for a filename, we rely on the Card logic to generate the text, 
            # but we need to create the file here.
            # Current Card logic expects `audio_source` string to generate filename `sanitize_filename(audio_source)...`
            # So we pass `audio_query` as `audio_source`.
            
            filename = f"{sanitize_filename(audio_query.lower())}_pronunciation.mp3"
            filepath = os.path.join("audio", filename)
            
            # For sentences, sanitize might be weird if very long. 
            # But sanitize_filename usually truncates or handles chars.
            # Let's trust sanitize_filename for now or check utils.
            
            tts_success = await openai_api.generate_speech(audio_query, filepath)
            if tts_success:
                audio_text_success = audio_query
            else:
                 audio_text_success = None

        # Create card
        return Card(
            card_id=index,
            source=source_text,
            translation=details.get("translation", []),
            context=details.get("context", []),
            gender=details.get("gender", ""),
            plural=details.get("plural", "") if input_type == "word" else "",
            input_type=input_type,
            tip=tip,
            audio_source=audio_text_success
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
                        f"[sound:{card.audio_filename}]"
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
                    # Expression format: expression + context
                    front_parts = []
                    if card.audio_filename:
                        front_parts.append(f"[sound:{card.audio_filename}]")
                    front_parts.append(card.source)

                    back_parts = [translation]

                    if card.context and card.context[0].get("german") != "N/A":
                        context_german = card.context[0]["german"]
                        context_english = card.context[0]["english"]
                        front_parts.append(f"<i>{context_german}</i>")
                        back_parts.append(f"<i>{context_english}</i>")

                else:  # sentence
                    # Sentence format: just sentence -> translation
                    front_parts = []
                    if card.audio_filename:
                        front_parts.append(f"[sound:{card.audio_filename}]")
                    front_parts.append(card.source)

                    back_parts = [translation]

                # Tip always at the bottom
                if card.tip:
                    back_parts.append(f"<br>💡 <i>{card.tip}</i>")

                front_field = "<br>".join(front_parts)
                back_field = "<br>".join(back_parts)

                # Write to file with a semicolon separator
                file.write(f"{front_field};{back_field}\n")

        print(f"Cards written to: {output_file_path}")
    except Exception as error:
        print(f"Error writing to output file: {error}")
        raise
