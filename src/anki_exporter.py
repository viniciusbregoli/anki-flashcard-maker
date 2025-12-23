"""
Module for creating Anki .apkg packages using genanki.
"""
import genanki
import random
import os
from typing import List
from line_processing import Card
from utils import sanitize_filename

# Generate a unique model ID (this should ideally be constant for updates, but random is fine for new decks)
# Using a fixed ID here to keep card type consistent if user regenerates
MODEL_ID = 1634523456
DECK_ID = 2654323456

def create_anki_package(cards: List[Card], output_filename: str = "anki-deck.apkg"):
    """
    Creates an Anki .apkg file from a list of Card objects.
    
    Args:
        cards: List of processed Card objects.
        output_filename: Name of the output .apkg file.
        
    Returns:
        The path to the generated package.
    """
    
    # 1. Define the Anki Model
    # We use a simple Basic model with Front and Back fields because existing logic 
    # already formats HTML strings for Front/Back.
    my_model = genanki.Model(
        MODEL_ID,
        'Simple Model (Reverso)',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Question}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ],
        css=""".card {
 font-family: arial;
 font-size: 20px;
 text-align: center;
 color: black;
 background-color: white;
}"""
    )

    # 2. Define the Deck
    my_deck = genanki.Deck(
        DECK_ID,
        'German Vocabulary'
    )

    # 3. Add Notes (Cards) and collect media files
    media_files = []
    
    for card in cards:
        # Re-use the existing logic to generate the HTML content for front/back
        front, back = _generate_card_html(card)
        
        # Add note to deck
        note = genanki.Note(
            model=my_model,
            fields=[front, back]
        )
        my_deck.add_note(note)
        
        # Check for audio file to include
        if card.input_type == "word":
            audio_filename = f"{sanitize_filename(card.source.lower())}_pronunciation.mp3"
            audio_path = os.path.join("audio", audio_filename)
            if os.path.exists(audio_path):
                media_files.append(audio_path)

    # 4. create the package
    my_package = genanki.Package(my_deck)
    my_package.media_files = media_files
    
    print(f"Generating package with {len(cards)} cards and {len(media_files)} media files...")
    my_package.write_to_file(output_filename)
    print(f"Verified package created at: {os.path.abspath(output_filename)}")
    
    return output_filename


def _generate_card_html(card: Card):
    """
    Helper to generate the HTML strings for Front and Back fields.
    Refactored from write_cards_to_file logic.
    """
    translation = ", ".join(card.translation)
    front_parts = []
    back_parts = [translation]

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
            f"[sound:{sanitize_filename(card.source.lower())}_pronunciation.mp3]"
        )

        front_parts = [
            f"{sound_field} {gender_display}{card.source}{plural_display}"
        ]
        
        if card.context and card.context[0].get("german") != "N/A":
            context_german = card.context[0]["german"]
            context_english = card.context[0]["english"]
            front_parts.append(f"<i>{context_german}</i>")
            back_parts.append(f"<i>{context_english}</i>")

    elif card.input_type == "expression":
        # Expression format: expression + context (no audio, no gender)
        front_parts = [card.source]
        
        if card.context and card.context[0].get("german") != "N/A":
            context_german = card.context[0]["german"]
            context_english = card.context[0]["english"]
            front_parts.append(f"<i>{context_german}</i>")
            back_parts.append(f"<i>{context_english}</i>")

    else:  # sentence
        # Sentence format: just sentence -> translation
        front_parts = [card.source]

    front_field = "<br>".join(front_parts)
    back_field = "<br>".join(back_parts)
    
    return front_field, back_field
