## AR Chat #######################################################################################################
## a class for creating a message board in OpenCV
class ARChat():
'''
An ARChat object outputs an array with a custom UI created by the Butcher Bros (spec. Michael) 

Public Functions:
    - post: posts a message to the ARChat
    - stage: stages a message to the user's staging area  
    - getPath: returns the path to the ARChat image   
'''
    def __init__(self, topic, chatrooms = []):
        '''
        Initialize a new ARChat.
        The ARChat always initializes with at least one board topic, "general"
        
        Inputs:
            - topic: the topic associated with each ARChat
            - chatrooms: a list of type str, which contains a string of currently active boards
        
        '''
        pass

    def post(self, user, message, color, time):
        '''
        Posts a message to be updated to the currently active board

        Inputs:
            - user (str): the name of the user who sent the message
            - message (str): the message sent by the user
            - color (tuple): the RGB tuple associated with the user
            - time (dict): dictionary with hour, minute, second
        '''
        pass

    def stage(self, message):
        '''
        Stages a message to the user's staging area
        
        Inputs:
            - message (str): the string to place in the user's message box
        '''
        pass

    def getPath(self):
        '''
        Returns a path to the saved ARChat .jpg
        '''
        pass