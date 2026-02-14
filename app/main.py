from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
import edge_tts
import io

app = FastAPI()

# Enable CORS so your app and website can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration for a realistic American male voice
# Andrew is one of the most human-sounding neural voices in 2026
VOICE = "en-US-AndrewNeural"

@app.get("/tts")
async def text_to_speech(
    text: str = Query(..., description="Text to convert"),
    rate: str = Query("-10%", description="Speed")
):
    try:
        # 1. Standardize the rate format (e.g., -10%)
        clean_rate = rate if '%' in rate else f"{rate}%"
        if not (clean_rate.startswith('-') or clean_rate.startswith('+')):
            clean_rate = f"+{clean_rate}"

        # 2. Generate the voice using the American Andrew voice
        # We skip the language detection to keep it strictly American English
        communicate = edge_tts.Communicate(text, VOICE, rate=clean_rate)
        
        # 3. Buffer the audio stream into memory
        # This is vital for mobile apps to prevent stuttering on 4G/5G
        audio_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]

        if not audio_bytes:
            raise HTTPException(status_code=500, detail="Audio generation failed")

        # 4. Return the response optimized for Mobile App buffering
        return Response(
            content=audio_bytes, 
            media_type="audio/mpeg",
            headers={
                "Content-Type": "audio/mpeg",
                "Content-Length": str(len(audio_bytes)),
                "Accept-Ranges": "bytes",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "public, max-age=3600" # Cache for 1 hour to save your Vercel usage
            }
        )
        
    except Exception as e:
        print(f"Backend Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"status": "Lucix American TTS System Online"}
