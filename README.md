# Reverso Anki

An AI-powered Python tool to automatically create German Anki flashcards. It uses the OpenAI API for translation, gender detection, and context sentences, and the Forvo API for audio pronunciations.

## Features

- **AI-Powered Translations**: Uses OpenAI (`gpt-4o`) for accurate German-to-English translations.
- **Multiple Input Types**: Supports single words, expressions, and complete sentences.
- **Smart Gender Detection**: AI determines the grammatical gender (`der`, `die`, `das`) for nouns.
- **AI Context Generation**: Automatically creates simple, natural example sentences for words and expressions.
- **Audio Pronunciations**: Fetches and embeds real human pronunciations from Forvo (for single words only).
- **Intelligent Processing**: Automatically detects input type and applies appropriate processing logic.
- **Fully Automated**: Processes mixed content from `input.txt` and generates ready-to-import Anki cards.

## Requirements

- Python 3.7+
- Forvo API Key (for audio)
- OpenAI API Key (for all text generation)

## Installation

1.  **Clone the repository and navigate into it.**
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set up API Keys:**
    -   Rename `env_template.txt` to `.env`.
    -   Add your Forvo and OpenAI API keys to the `.env` file.

## How to Use

1.  **Add Content**: Open `input.txt` and add your German content, one item per line:
    - Single words: `hauptbahnhof`
    - Expressions: `guten Tag`
    - Sentences: `Wie geht es dir?`
2.  **Run the Script**:
    ```bash
    python main.py
    ```
3.  **Import to Anki**:
    -   A new `output.txt` file will be created.
    -   Open Anki, go to `File > Import`, and select `output.txt`.
    -   The audio files in the `audio/` directory need to be manually moved to your Anki `collection.media` folder.

## Project Structure

```
openai-anki/
├── main.py                 # Main entry point
├── src/                    # Source code
│   ├── openai_api.py      # Handles all OpenAI API calls
│   └── ...                 # Other source files
├── utils/                  # Helper functions
├── input.txt               # Your German content (words, expressions, sentences)
├── output.txt              # Generated Anki cards
└── audio/                  # Downloaded .mp3 pronunciations
```
