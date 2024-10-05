from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import edge_tts
import asyncio
import os
import uuid

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-url.onrender.com"],  # Update this with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TTSRequest(BaseModel):
    text: str
    voice: str

@app.get("/")
async def read_root():
    return {"status": "healthy"}

@app.post("/api/tts")
async def convert_tts(request: TTSRequest):
    try:
        # Create temp directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)
        
        # Generate a unique filename
        file_name = f"temp/tts_{uuid.uuid4()}.mp3"
        
        # Convert text to speech
        communicate = edge_tts.Communicate(request.text, voice=request.voice)
        await communicate.save(file_name)
        
        # Return the audio file
        return FileResponse(
            file_name,
            media_type="audio/mpeg",
            filename="tts_output.mp3",
            background=asyncio.create_task(cleanup_file(file_name))
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def cleanup_file(file_name: str):
    await asyncio.sleep(60)  # Wait for file to be sent
    try:
        os.remove(file_name)
    except:
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
