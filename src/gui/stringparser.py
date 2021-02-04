## String Parser #######################################################################################################
## some nice code made by the one and only n10

def parse_string(phrase:str, marker:str, validNames):
    delim = marker
    words = phrase.split()
    hitlist = []
    indlist = []
    for index,word in enumerate(words):
        try:
            if (word == delim) and (words[index+1] in validNames.keys()):
                hitlist.append(validNames[words[index+1]])
                indlist.insert(0, index)
                indlist.insert(0, index+1)
        except IndexError:
            continue

    for ind in indlist:
        del words[ind]

    return (' '.join(words), hitlist)