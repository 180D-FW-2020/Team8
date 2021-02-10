from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class FSM:
    def __init__(self, phrase_signal, slots):
        self.detect = phrase_signal

        self.state_machine = QStateMachine()

        self.s_init = QState() # board not visible
        self.s_main = QState() # board becomes visible here
        self.s_msg = QState()
        self.s_msg_listen = QState(self.s_msg)
        self.s_msg_confirm = QState(self.s_msg)
        self.s_msg_send = QState(self.s_msg)
        self.s_msg.setInitialState(self.s_msg_listen)

        self.state_machine.addState(self.s_init)
        self.state_machine.addState(self.s_main)
        self.state_machine.addState(self.s_msg)
        self.state_machine.setInitialState(self.s_init)

        # signals, slots, and transitions
        self.s_init.entered.connect(slots[0]) # hide chatbox
        self.s_main.entered.connect(slots[1]) # display chatbox
        self.s_msg_listen.entered.connect(slots[2]) # message listen worker
        self.s_msg_send.entered.connect(slots[3]) # send message

        self.s_init.addTransition(signals[0], self.s_main) # 'start chatbox' displays chatbox
        self.s_main.addTransition(signals[1], self.s_msg) # 'send message' enters s_msg_listen
        self.s_main.addTransition(signals[2], self.s_init) # 'close chatbox' hides chatbox
        self.s_msg.addTransition(signals[3], self.s_main) # 'cancel message' backs out of s_msg at any substate
        self.s_msg_listen.addTransition(signals[4], self.s_msg_confirm) # wait until current phrase changes
        self.s_msg_confirm.addTransition(signals[5], self.s_msg_send) # 'yes' sends msg
        self.s_msg_confirm.addTransition(signals[6], self.s_msg_listen) # 'no' returns to listen
        self.s_msg_send.addTransition(self.s_main) # unconditional transition back to main

    def __phrase_option_handler__(self, state, handler):
        # when a new state is entered, connect the detect_phrase signal in the audio recognizer to the handler
        confirm_handle = lambda val=handler: self.detect.connect(val)
        state.entered.connect(confirm_handle)

        # when that state is exited, this is removed
        confirm_teardown = lambda val=handler: self.detect.disconnect(val)
        state.exited.connect(confirm_teardown)