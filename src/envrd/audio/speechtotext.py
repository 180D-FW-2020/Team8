### classes/methods for speech to text using pocketsphinx
# 
# 

import speech_recognition as speech
from threading import Thread
from queue import Queue

r = speech.Recognizer()
audio_queue = Queue()

def recognize_worker():
    # this runs in a background thread
    while True:
        audio = audio_queue.get()  # retrieve the next audio processing job from the main thread
        if audio is None: break  # stop processing if the main thread is done

        # received audio data, now recognize
        try:
            print("Sphinx heard: " + r.recognize_sphinx(audio))
        except speech.UnknownValueError:
            print("Sphinx could not understand audio")
        except speech.RequestError as err:
            print("Sphinx error; {0}".format(err))

        audio_queue.task_done()  # mark the audio processing job as completed in the queue


# start a new thread to recognize audio, while this thread focuses on listening
recognize_thread = Thread(target=recognize_worker)
recognize_thread.daemon = True
recognize_thread.start()
with speech.Microphone() as source:
    try:
        while True:  # repeatedly listen for phrases and put the resulting audio on the audio processing job queue
            audio_queue.put(r.listen(source))
    except KeyboardInterrupt:  # allow Ctrl + C to shut down the program
        pass

audio_queue.join()  # block until all current audio processing jobs are done
audio_queue.put(None)  # tell the recognize_thread to stop
recognize_thread.join()  # wait for the recognize_thread to actually stop