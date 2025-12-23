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
        self.model = "gpt-4o-mini"

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

    async def analyze_german_content(self, text: str) -> Dict[str, Any]:
        """
        Analyze the German text to automatically detect if it is a word, expression, or sentence,
        and provide the relevant details.
        """
        prompt = f"""
        Analyze the following German text: "{text}"
        
        1. Determine if it is a "word" (single noun/verb/adjective), "expression" (phrase/idiom), or "sentence" (complete thought).
        2. Provide the English translation.
        3. If it is a "word" (specifically a noun), provide the Gender (der, die, das) and Plural form. If not a noun or not applicable, write "N/A".
        4. If it is a "word" or "expression", provide a simple German Context Sentence and its English translation.
        5. If it is a "sentence", Context is not needed (write "N/A").
        6. Provide a short memory tip, etymology, compound word breakdown, OR grammar tip (e.g. usage note). IF none exists, write "N/A".

        Format strictly as:
        Type: [word/expression/sentence]
        Translation: [Text]
        Gender: [Text or N/A]
        Plural: [Text or N/A]
        German Context: [Text or N/A]
        English Context: [Text or N/A]
        Tip: [Text or N/A]
        """

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a German language expert. Analyze the input type intelligently.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.3,
        )

        content = response.choices[0].message.content.strip()
        return self._parse_analysis_response(content)

    async def generate_speech(self, text: str, output_path: str) -> bool:
        """
        Generate speech audio from text using OpenAI's new Audio model.
        """
        try:
            # We use the new chat completions audio capability
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini-audio-preview",
                modalities=["text", "audio"],
                audio={"voice": "ash", "format": "mp3"},
                messages=[
                    {"role": "user", "content": f"Please read the following German text naturally (just the text): {text}"}
                ]
            )
            
            # The audio data is returned as a base64 string in the response
            audio_data_b64 = response.choices[0].message.audio.data
            
            # Decode and write to file
            import base64
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(audio_data_b64))
                
            return True
        except Exception as e:
            print(f"Error generating OpenAI speech for '{text}': {e}")
            return False

    def _parse_analysis_response(self, response_text: str) -> Dict[str, Any]:
        """Parses the unified analysis response."""
        details = {}
        for line in response_text.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower().replace(" ", "_").replace("*", "")
                details[key] = value.strip()

        input_type = details.get("type", "word").lower()
        # Normalize input type just in case
        if "sentence" in input_type:
            input_type = "sentence"
        elif "expression" in input_type:
            input_type = "expression"
        else:
            input_type = "word"

        context = []
        if details.get("german_context", "N/A") != "N/A":
            context = [
                {
                    "german": details.get("german_context", "N/A"),
                    "english": details.get("english_context", "N/A"),
                }
            ]

        # Extract tip
        tip = details.get("tip", "N/A")
        if tip == "N/A":
            tip = ""

        return {
            "type": input_type,
            "translation": [details.get("translation", "N/A")],
            "gender": details.get("gender", "N/A") if details.get("gender") != "N/A" else "",
            "plural": details.get("plural", "N/A") if details.get("plural") != "N/A" else "",
            "context": context,
            "tip": tip
        }
