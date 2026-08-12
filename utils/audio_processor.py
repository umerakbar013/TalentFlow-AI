import time
from pathlib import Path

AUDIO_DIR = Path("data/audio_logs")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

def save_candidate_audio(audio_bytes: bytes, applicant_id: str, turn_id: int) -> str:
    """Saves raw audio securely to local disk."""
    timestamp = int(time.time())
    file_name = f"{applicant_id}_turn_{turn_id}_{timestamp}.wav"
    file_path = AUDIO_DIR / file_name
    
    with open(file_path, "wb") as f:
        f.write(audio_bytes)
        
    return str(file_path)

import speech_recognition as sr
import io

def transcribe_audio(audio_bytes: bytes) -> str:
    if not audio_bytes:
        return ""
    
    recognizer = sr.Recognizer()
    try:
        # Convert the Streamlit audio bytes into an AudioFile
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio_data = recognizer.record(source)
            # Actually transcribe your real voice using Google's free API
            text = recognizer.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        return "[Audio not understood. Please speak clearly.]"
    except Exception as e:
        return f"[Transcription error: {str(e)}]"