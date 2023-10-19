import speech_recognition as sr

# Create a recognizer instance
r = sr.Recognizer()

# Use the default microphone as the audio source
with sr.Microphone() as source:
    print("Listening...")
    # Read the audio data from the default microphone
    audio_data = r.record(source, duration=5)
    print("Recognizing...")
    # Convert speech to text
    text = r.recognize_google(audio_data)
    print(text)
