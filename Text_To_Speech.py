from gtts import gTTS
import io

def speak(text: str):
    tts = gTTS(text=text, lang="en")

    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)

    return audio_buffer
