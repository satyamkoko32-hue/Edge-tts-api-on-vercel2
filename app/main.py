from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
import io
import re

app = FastAPI()

# Fixes Mobile/Web connection issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def is_hindi(text):
    # Detects Hindi characters
    return bool(re.search(r'[\u0900-\u097F]', text))

@app.get("/tts")
async def text_to_speech(
    text: str = Query(..., description="Text to convert"),
    rate: str = Query("-10%", description="Speed")
):
    try:
        # 1. Clean the speed parameter
        clean_rate = rate if '%' in rate else f"{rate}%"
        
        # 2. Select High-Quality Neural Voices
        # 'Andrew' is the most realistic US English voice
        # 'Madhur' is the most realistic Hindi male voice
        voice = "hi-IN-MadhurNeural" if is_hindi(text) else "en-US-AndrewNeural"
        
        # 3. Generate the human-like audio
        communicate = edge_tts.Communicate(text, voice, rate=clean_rate)
        audio_data = io.BytesIO()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        
        audio_data.seek(0)
        return StreamingResponse(audio_data, media_type="audio/mpeg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def health():
    return {"status": "Online", "voice_engine": "Neural human v2"}
