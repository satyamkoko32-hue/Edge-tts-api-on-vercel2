from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
import io
import re

app = FastAPI()

# CRITICAL: This allows your mobile website to talk to your Vercel backend
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
        clean_rate = rate if '%' in rate else f"{rate}%"
        voice = "hi-IN-MadhurNeural" if is_hindi(text) else "en-US-AndrewNeural"
        
        communicate = edge_tts.Communicate(text, voice, rate=clean_rate)
        audio_data = io.BytesIO()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        
        audio_data.seek(0)
        
        # Return as a proper MP3 stream that mobile browsers recognize
        return StreamingResponse(
            audio_data, 
            media_type="audio/mpeg",
            headers={
                "Content-Type": "audio/mpeg",
                "Accept-Ranges": "bytes"
            }
        )
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
