from audio import *

phrases = {'testing':False}
capturing = True
rec = SpeechRecognizer(phrases)
rec.listenForPhrases()

while capturing:
    det = False
    for phrase, found in rec.phrases.items():
        if found:
            print("FOUND: " + phrase)
            det = True
            rec.resetDetection(phrase)
            break
    if det:
        break

rec.teardown()
rec.listenForPhrases()

while capturing:
    det = False
    for phrase, found in rec.phrases.items():
        if found:
            print("FOUND: " + phrase)
            det = True
            rec.resetDetection(phrase)
            break
    if det:
        break

del rec
