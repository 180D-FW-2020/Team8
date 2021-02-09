## AR Chat #######################################################################################################
## a class for creating a message board in OpenCV
class ARChat():
'''
An ARChat object outputs a 480p(?) array with a custom UI created by the Butcher Bros (spec. Michael) 

Public Members:
    - topics: a dictionary (or list?) mapping board topics to...?    
'''
    def __init__(self, topics):
        '''
        Initialize a new ARChat.
        The ARChat always initializes with at least one board topic, "general"
        
        Inputs:
            - topics: a list of type str, which contains the names of currently active boards
        
        '''
        pass

    def write(self, topic, user, message, color, time):
        '''
        Writes a message to be updated to the currently active board

        Inputs:
            - user (str): the name of the user who sent the message
            - message (str): the message sent by the user
            - color (tuple): the RGB tuple associated with the user
            - time (dict): dictionary with hour, minute, second
        
        Returns:
            - chat: an np.ndarray at 480p(?) of the chat with the modified message
        '''
        pass

    def userWrite(self, message):
        '''
        Writes out a message to the user's type-out message box
        
        Inputs:
            - message (str): the string to place in the user's message box
        
        Returns:
            - chat: an np.ndarray at 480p(?) of the chat with the modified message
        '''
        pass

    def switchTopic(self, topic):
        '''
        Switches the current topic displayed
        
        Inputs:
            - topic: a str with the name of the topic to switch to
        
        Returns:
            - None
        
        Errors(?):
            - LookupError: raised when the topic input is not in the boards dictionary (or list?)
        '''
        pass