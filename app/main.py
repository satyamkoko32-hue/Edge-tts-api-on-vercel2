from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
import edge_tts
import io
import httpx # You may need to add this to requirements.txt

app = FastAPI()

@app.get("/tts")
async def text_to_speech(
    text: str = Query(..., description="The text to convert to speech"),
    voice: str = Query("en-US-GuyNeural", description="Voice ID"),
    rate: str = Query("-10%", description="The speed of the voice")
):
    try:
        # Fix: Ensure rate always ends with %
        clean_rate = rate if '%' in rate else f"{rate}%"
        
        # 1. GET CHAT RESPONSE FROM OPENAI (Directly in backend for stability)
        # Using the new 2026 stable endpoint
        brain_url = f"https://gen.pollinations.ai/prompt/{text}?model=openai"
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(brain_url)
            if resp.status_code != 200:
                raise Exception("AI Brain is currently offline")
            ai_text = resp.text.replace('*', '').replace('#', '').strip()

        # 2. GENERATE SPEECH
        communicate = edge_tts.Communicate(ai_text, voice, rate=clean_rate)
        audio_data = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        
        audio_data.seek(0)
        return StreamingResponse(audio_data, media_type="audio/mpeg")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
