"""
Audio download module for getting pronunciation files from Forvo API.
"""

import os
import requests
import xml.etree.ElementTree as ET
from typing import Optional
from utils.utils import ensure_directory_exists, sanitize_filename


class AudioDownloader:
    """Handles downloading pronunciation audio files."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://apifree.forvo.com"

    async def download_pronunciation(
        self, word: str, language: str = "de", card_id: int = None
    ) -> bool:
        """
        Download MP3 pronunciation for a given word.

        Args:
            word (str): Word to get pronunciation for
            language (str): Language code (default: "de" for German)
            card_id (int): ID of the card for logging

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Define the API endpoint
            api_url = f"{self.base_url}/key/{self.api_key}/format/xml/action/standard-pronunciation/word/{word}/language/{language}"

            # Make the API request
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()

            # Parse the XML response
            root = ET.fromstring(response.text)

            # Find the first pronunciation item
            items = root.findall(".//item")
            if not items:
                print(f"  No pronunciation found for '{word}'")
                return False

            # Get the MP3 path from the first item
            path_mp3_elem = items[0].find("pathmp3")
            if path_mp3_elem is None or not path_mp3_elem.text:
                print(f"  No MP3 path found for '{word}'")
                return False

            mp3_url = path_mp3_elem.text

            # Download the MP3 file
            mp3_response = requests.get(mp3_url, timeout=30)
            mp3_response.raise_for_status()

            # Ensure the output directory exists
            output_dir = "audio"
            ensure_directory_exists(output_dir)

            # Save the MP3 file
            filename = f"{sanitize_filename(word)}_pronunciation.mp3"
            file_path = os.path.join(output_dir, filename)

            with open(file_path, "wb") as f:
                f.write(mp3_response.content)

            print(f"  ✓ Audio downloaded for '{word}'")
            return True

        except Exception as error:
            print(f"  ✗ Error downloading pronunciation for '{word}': {error}")
            return False


# Global instance for easy access
_audio_downloader = None


def get_audio_downloader(api_key: str) -> AudioDownloader:
    """Get or create the global audio downloader instance."""
    global _audio_downloader
    if _audio_downloader is None:
        _audio_downloader = AudioDownloader(api_key)
    return _audio_downloader


async def download_pronunciation(
    word: str, language: str = "de", card_id: int = None
) -> bool:
    """
    Convenience function to download pronunciation.

    Args:
        word (str): Word to get pronunciation for
        language (str): Language code
        card_id (int): Card ID for logging

    Returns:
        bool: True if successful, False otherwise
    """
    # Get API key from environment
    api_key = os.getenv("API_KEY")
    if not api_key:
        print(
            "  ⚠️  API_KEY not found in environment variables. Skipping audio download."
        )
        return False

    downloader = get_audio_downloader(api_key)
    return await downloader.download_pronunciation(word, language, card_id)
