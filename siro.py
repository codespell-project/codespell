import speech_recognition as sr
import pyttsx3

# Create a recognizer instance
recognizer = sr.Recognizer()

# Create a text-to-speech engine
engine = pyttsx3.init()


# Define a function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()


# Define a function to listen for voice input
def listen():
    with sr.Microphone() as source:
        audio = recognizer.listen(source)

    # Convert the captured voice input to text
    try:
        text = recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        text = "Could not understand audio"
    except sr.RequestError as e:
        text = "Could not request results from Google Speech Recognition service; {0}".format(
            e
        )

    return text


# Start the voice assistant loop
while True:
    # Listen for voice input
    text = listen()

    # Speak the recognized text
    speak(text)

    # Take action based on the recognized text
    # For example, if the user says "Open Google Chrome", you could open the Google Chrome web browser
