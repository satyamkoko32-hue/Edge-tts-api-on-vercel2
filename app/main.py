from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
import edge_tts
import io

app = FastAPI()

# Recommended "Real Human" Voice IDs
# Hindi (India): hi-IN-MadhurNeural (Male), hi-IN-SwaraNeural (Female)
# English (US): en-US-GuyNeural (Male), en-US-AvaNeural (Female)

@app.get("/tts")
async def text_to_speech(
    text: str = Query(..., description="The text to convert to speech"),
    voice: str = Query("hi-IN-MadhurNeural", description="Voice ID (e.g., hi-IN-MadhurNeural or en-US-AvaNeural)"),
    rate: str = Query("+0%", description="Speed: use numbers like -10 or +20")
):
    try:
        # --- AUTO-FIX FOR INVALID RATE ERROR ---
        # Ensure rate has a '+' or '-' and always ends with '%'
        clean_rate = rate.strip()
        if '%' not in clean_rate:
            if not clean_rate.startswith(('-', '+')):
                clean_rate = f"+{clean_rate}%"
            else:
                clean_rate = f"{clean_rate}%"
        
        # Create the TTS object with the cleaned rate
        communicate = edge_tts.Communicate(text, voice, rate=clean_rate)
        
        audio_data = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        
        audio_data.seek(0)
        return StreamingResponse(audio_data, media_type="audio/mpeg")
    
    except Exception as e:
        # Detailed error reporting
        raise HTTPException(status_code=500, detail=f"TTS Error: {str(e)}")

@app.get("/")
async def read_root():
    return {"status": "Online", "voices": ["hi-IN-MadhurNeural", "en-US-AvaNeural"]}
