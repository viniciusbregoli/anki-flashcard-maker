from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import sys
import os
import shutil
import zipfile
import asyncio
import json

from dotenv import load_dotenv

# Add src to python path to allow imports to work as they do in the CLI script
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

from line_processing import generate_cards, cleanup_previous_audio, write_cards_to_file
from src.anki_exporter import create_anki_package

app = FastAPI(title="Reverso Anki API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure audio directory exists
if not os.path.exists("audio"):
    os.makedirs("audio")
app.mount("/api/audio", StaticFiles(directory="audio"), name="audio")

class WordsRequest(BaseModel):
    words: List[str]

@app.post("/api/generate")
async def generate_cards_endpoint(request: WordsRequest):
    """
    Accepts a list of words, processes them, generating cards AND the Anki package.
    Returns a stream of progress updates using Server-Sent Events (SSE).
    """
    if not request.words:
        raise HTTPException(status_code=400, detail="No words provided")
    
    async def event_generator():
        q = asyncio.Queue()

        # Simple async function, NOT a generator, so it can be awaited
        async def progress_callback(current, total, word):
            data = json.dumps({
                "type": "progress",
                "current": current + 1,
                "total": total,
                "percent": int(((current) / total) * 100),
                "word": word
            })
            await q.put(f"data: {data}\n\n")

        # Wrapper to run generation and return result or exception
        async def run_generation():
            try:
                # Clean up old audio before starting
                cleanup_previous_audio()
                return await generate_cards(request.words, progress_callback=progress_callback)
            except Exception as e:
                return e

        task = asyncio.create_task(run_generation())
        
        try:
            while not task.done():
                try:
                    # Poll queue with timeout to allow checking task status
                    item = await asyncio.wait_for(q.get(), timeout=0.1)
                    yield item
                except asyncio.TimeoutError:
                    continue

            # Flush any remaining items
            while not q.empty():
                yield await q.get()

            # Check result
            result = await task
            
            if isinstance(result, Exception):
                raise result # Re-raise to be caught by outer except
            
            cards = result
            
            # Create Anki Package
            create_anki_package(cards, output_filename="anki-deck.apkg")
            write_cards_to_file(cards, "output.txt")
            
            # Final success event
            final_data = json.dumps({
                "type": "result",
                "status": "success",
                "count": len(cards),
                "cards": [card.to_dict() for card in cards]
            })
            yield f"data: {final_data}\n\n"
            
        except Exception as e:
            print(f"Error in generate_cards_endpoint: {e}")
            import traceback
            traceback.print_exc()
            error_data = json.dumps({
                "type": "error",
                "message": str(e)
            })
            yield f"data: {error_data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

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

class SingleCardRequest(BaseModel):
    word: str
    id: int

from src.openai_api import OpenAIAPI
from line_processing import process_line

@app.post("/api/regenerate-card")
async def regenerate_card_endpoint(request: SingleCardRequest):
    """
    Regenerates a single card for a given word.
    """
    try:
        openai_api = OpenAIAPI()
        # We reuse process_line. It downloads audio and generates content.
        # It handles overwriting audio file if filename is same.
        card = await process_line(request.word, request.id, openai_api)
        
        if not card:
             raise HTTPException(status_code=500, detail="Failed to regenerate card")

        return {
            "status": "success",
            "card": card.to_dict()
        }
    except Exception as e:
        print(f"Error regenerating card: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount React Frontend (Must be last to avoid overriding API routes)
# Check if the build directory exists (production mode)
if os.path.exists("web/dist"):
    app.mount("/", StaticFiles(directory="web/dist", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8081, reload=True)
