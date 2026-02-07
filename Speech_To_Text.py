import speech_recognition as sr

def get_text():
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("Say something!")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source)

        text = recognizer.recognize_google(audio)
        return text

    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        return f"API error: {e}"
