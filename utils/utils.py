"""
Utility functions for the Reverso Anki project.
"""

import os


def read_input_file(file_path):
    """
    Read the input file and return a list of words.

    Args:
        file_path (str): Path to the input file

    Returns:
        list: List of words from the input file
    """
    try:
        if not os.path.exists(file_path):
            print(f"Input file not found: {file_path}")
            return []

        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content:
                print("Input file is empty.")
                return []

            lines = [line.strip() for line in content.split("\n") if line.strip()]
            return lines

    except Exception as e:
        print(f"Error reading input file: {e}")
        return []


def capitalize_string(text):
    """
    Capitalize the first letter of a string and make the rest lowercase.

    Args:
        text (str): Input text

    Returns:
        str: Capitalized text
    """
    if not text:
        return ""
    return text[0].upper() + text[1:].lower() if len(text) > 1 else text.upper()


def ensure_directory_exists(directory_path):
    """
    Ensure a directory exists, create it if it doesn't.

    Args:
        directory_path (str): Path to the directory
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Created directory: {directory_path}")


def sanitize_filename(filename):
    """
    Sanitize a filename by replacing spaces with underscores.

    Args:
        filename (str): Original filename

    Returns:
        str: Sanitized filename
    """
    return filename.replace(" ", "_")


def detect_input_type(text):
    """
    Detect if the input is a single word, expression, or sentence.

    Args:
        text (str): Input text to analyze

    Returns:
        str: 'word', 'expression', or 'sentence'
    """
    text = text.strip()

    # Check for sentence indicators
    if any(text.endswith(punct) for punct in [".", "!", "?"]):
        return "sentence"

    # Count words (split by spaces)
    words = text.split()

    # Single word
    if len(words) == 1:
        return "word"

    # Multiple words without sentence punctuation = expression
    return "expression"
