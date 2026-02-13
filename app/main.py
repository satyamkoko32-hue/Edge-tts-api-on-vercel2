from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
import edge_tts
import io

app = FastAPI()

@app.get("/tts")
async def text_to_speech(
    text: str = Query(..., description="The text to convert to speech"),
    voice: str = Query("hi-IN-MadhurNeural", description="The voice to use"),
    rate: str = Query("+0%", description="The speed of the voice")
):
    try:
        # Create the TTS object
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        
        # Stream the audio data into a buffer
        audio_data = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        
        audio_data.seek(0)
        
        # Return direct MP3 audio
        return StreamingResponse(audio_data, media_type="audio/mpeg")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {"status": "Online", "endpoint": "/tts"}
