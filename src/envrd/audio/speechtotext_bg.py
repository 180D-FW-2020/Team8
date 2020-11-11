import speech_recognition as sr
import time

# this is called from the background thread
def callback(recognizer, audio):
    # received audio data, now we'll recognize it
    try:
        recog = r.recognize_sphinx(audio)
        print("Sphinx heard: " + recog)
    except speech.UnknownValueError:
        print("Sphinx could not understand audio")
    except speech.RequestError as err:
        print("Sphinx error; {0}".format(err))

    if "testing" in recog:
        print("KEYPHRASE (testing) DETECTED")

r = sr.Recognizer()
m = sr.Microphone()
with m as source:
    r.adjust_for_ambient_noise(source)  # we only need to calibrate once, before we start listening

# start listening in the background (note that we don't have to do this inside a `with` statement)
stop_listening = r.listen_in_background(m, callback)

while(1):
    time.sleep(0.1)
# calling this function requests that the background listener stop listening
# while(1):
#     out = input("")
#     if "q" in out:
#         stop_listening(wait_for_stop=False)

