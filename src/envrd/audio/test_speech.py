import speech_recognition as speech
import sphinxbase
import pocketsphinx

r = speech.Recognizer()
with speech.Microphone(sample_rate=44100) as source:
    print("listening...")
    audio = r.listen(source)

try:
    print("Sphinx heard: " + r.recognize_sphinx(audio))
except speech.UnknownValueError:
    print("Sphinx could not understand audio")
except speech.RequestError as err:
    print("Sphinx error; {0}".format(err))
    