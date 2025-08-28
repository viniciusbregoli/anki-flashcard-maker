# OpenAI Anki

An AI-powered Python tool to automatically create German Anki flashcards. It uses the OpenAI API for translation, gender detection, and context sentences, and the Forvo API for audio pronunciations.

## Features

- **AI-Powered Translations**: Uses OpenAI (`gpt-4o`) for accurate German-to-English translations.
- **Smart Gender Detection**: AI determines the grammatical gender (`der`, `die`, `das`) of each noun.
- **AI Context Generation**: Automatically creates simple, natural example sentences for each word.
- **Audio Pronunciations**: Fetches and embeds real human pronunciations from Forvo.
- **Fully Automated**: Processes a list of words from `input.txt` and generates ready-to-import Anki cards.

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

1.  **Add Words**: Open `input.txt` and add your list of German words, one word per line.
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
├── input.txt               # Your list of German words
├── output.txt              # Generated Anki cards
└── audio/                  # Downloaded .mp3 pronunciations
```
