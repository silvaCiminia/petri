#!/usr/bin/env python3


class Session:
    def __init__(self,
                 name: str = None,
                 item_dict: dict = {}
                 ):
        self.name = name
        self.item_dict = item_dict


class PetriClass:
    # The base class from which all classes to be stored must inherit
    def __init__(self,
                 id: str = None,
                 session: Session = None):
        # Must have an empty __init__ method declaring a blank ID
        # and session. This will be used to store object references
        self.id = id
        self.session = session
