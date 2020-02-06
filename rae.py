"""
aim callback updates state, and/or queues child aims
"""

class RefinementActingEngine(object):
    pass

class Aim(object):
    def __init__(self, name, arguments, callback, preconditions, postconditions):
        """
        name: a string identifier
        arguments: a list of arguments (along with current state)
        callback: a function repeatedly called on the current state and arguments while the aim is active
        preconditions: a list of boolean-valued functions of initial state and arguments that must be true to perform this aim
        preconditions: a list of boolean-valued functions of current state and arguments that must be true to finish this aim
        """
        self.name = name
        self.arguments = arguments
        self.callback = callback
        self.preconditions = preconditions
        self.postconditions = postconditions

class AimTree(object):
    def __init__(self, aim):        
        

