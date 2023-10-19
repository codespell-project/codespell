import speech_recognition as sr

# Create a recognizer instance
recognizer = sr.Recognizer()

# Capture voice input from the microphone
with sr.Microphone() as source:
    audio = recognizer.listen(source)

# Convert the captured voice input to text
try:
    text = recognizer.recognize_google(audio)
except sr.UnknownValueError:
    print("Could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))

# Print the recognized text
print(text)
