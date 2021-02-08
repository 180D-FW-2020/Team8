## Globals #######################################################################################################
## a list of global constructions/frameworks for MEAT

## MSG #######################################################################################################
## the dictionary structure of all message packets over MEAT mqtt
MSG = {
            "message_type" : str,
            "user" : str,
            "data" : str,
            "time" : {
                "hour": int,
                "minute": int,
                "second": int
            },
            "ID" : int
        }

## EMOTEIDS #######################################################################################################
## a dictionary of the emote IDs, as used to convey which emote to display with the emote animation framework

EMOTEIDS = {
   1 : ":/emotes/angry",
   2 : ":/emotes/cringe",
   3 : ":/emotes/cry",
   4 : ":/emotes/doubt",
   5 : ":/emotes/LOL",
   6 : ":/emotes/welp",
   7 : ":/emotes/frown",
   8 : ":/emotes/grin",
   9 : ":/emotes/love",
   10 : ":/emotes/ofcourse",
   11 : ":/emotes/shock",
   12 : ":/emotes/simp",
   13 : ":/emotes/smile",
   14 : ":/emotes/hmmm",
   15 : ":/emotes/tongue",
   16 : ":/emotes/wink"
}