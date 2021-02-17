import sys
import stringparser

EMOTEIDS = {
    "angry"        : 1 ,
    "cringe"       : 2 ,
    "cry"          : 3 ,
    "doubt"        : 4 ,
    "LOL"          : 5 ,
    "welp"         : 6 ,
    "frown"        : 7 ,
    "grin"         : 8 ,
    "love"         : 9 ,
    "ofcourse"     : 10,           
    "shock"        : 11,
    "simp"         : 12,
    "smile"        : 13,
    "hmmm"         : 14,
    "tongue"       : 15,
    "wink"         : 16        
            }

if __name__ == "__main__":
    msg = "This is fun slash angry"
    txt, emojis = stringparser.parse_string(msg, "slash", EMOTEIDS)
    print(txt, '\n', emojis)            # should print "This is fun", newline, [1]