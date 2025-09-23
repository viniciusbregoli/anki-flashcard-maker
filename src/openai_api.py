"""
OpenAI API client for translation, gender detection, and context generation.
"""

import os
import openai
from typing import Dict, Any


class OpenAIAPI:
    """Client for OpenAI services to handle language tasks."""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. Please add it to your .env file."
            )

        # Use the async client
        self.client = openai.AsyncOpenAI(api_key=self.openai_api_key)
        self.model = "gpt-4o"

    async def get_word_details(self, word: str) -> Dict[str, Any]:
        """
        Get translation, gender, and context for a German word using a single async OpenAI call.
        """
        prompt = f"""
        Analyze the German word: "{word}"
        Provide:
        1. English Translation
        2. Grammatical Gender (der, die, or das)
        3. Plural form (if applicable, or "N/A" if no plural exists)
        4. A simple German Context Sentence
        5. The English translation of that sentence
        Format as:
        Translation: [Text]
        Gender: [Text]
        Plural: [Text]
        German Context: [Text]
        English Context: [Text]
        """

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a German language expert. Provide concise, accurate info.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.3,
        )

        content = response.choices[0].message.content.strip()
        return self._parse_openai_response(content)

    async def get_expression_details(self, expression: str) -> Dict[str, Any]:
        """
        Get translation and context for a German expression using a single async OpenAI call.
        """
        prompt = f"""
        Analyze the German expression: "{expression}"
        Provide:
        1. English Translation
        2. A simple German Context Sentence using this expression
        3. The English translation of that context sentence
        Format as:
        Translation: [Text]
        German Context: [Text]
        English Context: [Text]
        """

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a German language expert. Provide concise, accurate translations and natural context examples.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
            temperature=0.3,
        )

        content = response.choices[0].message.content.strip()
        return self._parse_expression_response(content)

    async def get_sentence_details(self, sentence: str) -> Dict[str, Any]:
        """
        Get translation for a German sentence using a single async OpenAI call.
        """
        prompt = f"""
        Translate the German sentence to English: "{sentence}"
        Provide only:
        1. English Translation
        Format as:
        Translation: [Text]
        """

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a German language expert. Provide accurate, natural translations.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.3,
        )

        content = response.choices[0].message.content.strip()
        return self._parse_sentence_response(content)

    def _parse_openai_response(self, response_text: str) -> Dict[str, Any]:
        """Parses the structured response from the OpenAI API for words."""
        details = {}
        for line in response_text.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower().replace(" ", "_")
                details[key] = value.strip()

        return {
            "translation": [details.get("translation", "N/A")],
            "gender": details.get("gender", "N/A"),
            "plural": details.get("plural", "N/A"),
            "context": [
                {
                    "german": details.get("german_context", "N/A"),
                    "english": details.get("english_context", "N/A"),
                }
            ],
        }

    def _parse_expression_response(self, response_text: str) -> Dict[str, Any]:
        """Parses the structured response from the OpenAI API for expressions."""
        details = {}
        for line in response_text.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower().replace(" ", "_")
                details[key] = value.strip()

        return {
            "translation": [details.get("translation", "N/A")],
            "gender": "",  # No gender for expressions
            "context": [
                {
                    "german": details.get("german_context", "N/A"),
                    "english": details.get("english_context", "N/A"),
                }
            ],
        }

    def _parse_sentence_response(self, response_text: str) -> Dict[str, Any]:
        """Parses the structured response from the OpenAI API for sentences."""
        details = {}
        for line in response_text.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower().replace(" ", "_")
                details[key] = value.strip()

        return {
            "translation": [details.get("translation", "N/A")],
            "gender": "",  # No gender for sentences
            "context": [],  # No additional context for sentences
        }
