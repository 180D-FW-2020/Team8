from audio import SpeechRecognizer

sped = SpeechRecognizer()
phrase = "testing"
sped.add_keyphrase(phrase)

inc = 0

while(1):
    for phrase,detected in sped.phrases.items():
        if detected == True:
            #this is the detection event. do whatever needs to be done once a keyphrase is detected here
            print("KEYPHRASE \"{0}\" DETECTED".format(phrase))
            inc += 1
    #print(sped.phrases)
    sped.reset_detect_events()

    if inc > 2:
        break
    