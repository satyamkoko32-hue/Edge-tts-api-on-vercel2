from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
import io
import re

app = FastAPI()

# Enable CORS so your website can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def is_hindi(text):
    # Detects Devanagari (Hindi) characters
    return bool(re.search(r'[\u0900-\u097F]', text))

@app.get("/tts")
async def text_to_speech(
    text: str = Query(..., description="The text to convert to speech"),
    rate: str = Query("-10%", description="The speed of the voice")
):
    try:
        # 1. CLEAN RATE: Ensure it always has the % sign
        clean_rate = rate if '%' in rate else f"{rate}%"
        if not clean_rate.startswith(('-', '+')):
            clean_rate = f"+{clean_rate}"
        
        # 2. SELECT THE MOST REALISTIC NEURAL VOICES
        # English: 'en-US-AndrewNeural' is very high quality/human
        # Hindi: 'hi-IN-MadhurNeural' is the standard for natural male voice
        voice = "hi-IN-MadhurNeural" if is_hindi(text) else "en-US-AndrewNeural"
        
        # 3. GENERATE SPEECH
        communicate = edge_tts.Communicate(text, voice, rate=clean_rate)
        audio_data = io.BytesIO()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        
        audio_data.seek(0)
        
        # 4. RETURN MP3 STREAM
        return StreamingResponse(
            audio_data, 
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename='speech.mp3'"}
        )
    
    except Exception as e:
        print(f"Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"status": "Online", "model": "Neural-Human-V2"}
