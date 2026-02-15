from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
import uvicorn

app = FastAPI()

# Full CORS fix for Vercel and Browser testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2026 Human-Tier Neural Voice
# Andrew is great, Brian is also a top-tier alternative for 'Human' feel
VOICE = "en-US-AndrewNeural"

@app.get("/tts")
async def text_to_speech(
    text: str = Query(..., description="Text to convert"),
    rate: str = Query("-10%", description="Speed: e.g. -10%"),
    pitch: str = Query("+0Hz", description="Pitch: e.g. +2Hz for more energy")
):
    try:
        # 1. Clean and validate inputs
        # Ensures rate always has a % and a sign
        clean_rate = rate if '%' in rate else f"{rate}%"
        if not (clean_rate.startswith('-') or clean_rate.startswith('+')):
            clean_rate = f"+{clean_rate}"

        # 2. Humanization Logic
        # We use Communicate with specific prosody for a more 'natural' flow
        communicate = edge_tts.Communicate(
            text=text, 
            voice=VOICE, 
            rate=clean_rate, 
            pitch=pitch
        )
        
        # 3. Stream and Buffer
        audio_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]

        if not audio_bytes:
            raise HTTPException(status_code=500, detail="Neural engine returned no data")

        # 4. Professional Audio Headers
        return Response(
            content=audio_bytes, 
            media_type="audio/mpeg",
            headers={
                "Content-Type": "audio/mpeg",
                "Content-Length": str(len(audio_bytes)),
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "public, max-age=86400" # Cache for 24 hours (Saves Vercel execution time)
            }
        )
        
    except Exception as e:
        print(f"Neural Error: {e}")
        raise HTTPException(status_code=500, detail="Voice System Offline")

@app.get("/")
async def root():
    return {
        "status": "Online",
        "voice_engine": "Lucix Human Neural v2",
        "sample_usage": "/tts?text=Hello Prabhat, system is working&rate=-5%"
    }
