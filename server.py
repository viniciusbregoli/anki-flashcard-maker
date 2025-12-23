from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import sys
import os
import shutil
import zipfile
import asyncio

from dotenv import load_dotenv

# Add src to python path to allow imports to work as they do in the CLI script
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

from line_processing import generate_cards, cleanup_previous_audio, write_cards_to_file

app = FastAPI(title="Reverso Anki API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
# Ensure audio directory exists
if not os.path.exists("audio"):
    os.makedirs("audio")
app.mount("/api/audio", StaticFiles(directory="audio"), name="audio")

class WordsRequest(BaseModel):
    words: List[str]

from src.anki_exporter import create_anki_package

# ... existing imports ...

@app.post("/api/generate")
async def generate_cards_endpoint(request: WordsRequest):
    """
    Accepts a list of words, processes them, generating cards AND the Anki package.
    """
    if not request.words:
        raise HTTPException(status_code=400, detail="No words provided")
    
    try:
        # Clean up old audio before starting a new batch
        cleanup_previous_audio()
        
        # Process the cards
        # Note: This will download audio to the 'audio/' directory
        cards = await generate_cards(request.words)
        
        # Create Anki Package (.apkg)
        # This function packages the cards and the audio files into a single importable file
        create_anki_package(cards, output_filename="anki-deck.apkg")
        
        # Also create output.txt as backup/reference (optional)
        write_cards_to_file(cards, "output.txt")
        
        # Return the card data as JSON for preview
        return {
            "status": "success",
            "count": len(cards),
            "cards": [card.to_dict() for card in cards]
        }
        
    except Exception as e:
        print(f"Error in generate_cards_endpoint: {e}")
        # Print full stack trace for debugging
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download")
async def download_package():
    """
    Returns the generated .apkg file.
    """
    try:
        file_path = "anki-deck.apkg"
        if os.path.exists(file_path):
             return FileResponse(file_path, media_type="application/octet-stream", filename="german-vocabulary.apkg")
        else:
            raise HTTPException(status_code=404, detail="Package not found. Generate cards first.")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount React Frontend (Must be last to avoid overriding API routes)
# Check if the build directory exists (production mode)
if os.path.exists("web/dist"):
    app.mount("/", StaticFiles(directory="web/dist", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8081, reload=True)
