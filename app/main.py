from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
import io
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def is_hindi(text):
    return bool(re.search(r'[\u0900-\u097F]', text))

@app.get("/tts")
async def text_to_speech(
    text: str = Query(..., description="Text to convert"),
    rate: str = Query("-10%", description="Speed")
):
    try:
        # 1. Clean formatting for Edge-TTS
        clean_rate = rate if '%' in rate else f"{rate}%"
        if not clean_rate.startswith(('-', '+')):
            clean_rate = f"+{clean_rate}"

        # 2. Voices: Andrew (US English) and Madhur (Hindi)
        voice = "hi-IN-MadhurNeural" if is_hindi(text) else "en-US-AndrewNeural"
        
        # 3. Generate audio
        communicate = edge_tts.Communicate(text, voice, rate=clean_rate)
        
        # We collect all bytes first to ensure the mobile app gets a complete file
        audio_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]

        # 4. Return as a full file response (Best for Mobile Apps)
        return Response(
            content=audio_bytes, 
            media_type="audio/mpeg",
            headers={
                "Content-Type": "audio/mpeg",
                "Content-Length": str(len(audio_bytes)),
                "Accept-Ranges": "bytes",
                "Connection": "keep-alive",
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
