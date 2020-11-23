from audio import SpeechRecognizer
import time

sped = SpeechRecognizer()
phrase = "testing"
sped.add_keyphrase(phrase)

while(1):
    time.sleep(0.5)
    for phrase,detected in sped.phrases.items():
        if detected == True:
            #this is the detection event. do whatever needs to be done once a keyphrase is detected here
            print("KEYPHRASE \"{0}\" DETECTED".format(phrase))
    #print(sped.phrases)
    sped.reset_detect_events()
    