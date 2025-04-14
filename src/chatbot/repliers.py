from abc import abstractmethod

from .types import *

class Replier:
    """
    A replier takes a request and replies with a string and a set
    of choices to react to the reply.
    """
    def __init__(self) -> None:
        self.END_REPLY = Reply("Schönen Tag noch!", [])

    @abstractmethod
    def reply(self, request: str) -> Reply:
        return EmptyReply()

class DummyReplier(Replier):
    def reply(self, request: str) -> Reply:
        stopOption = "Chat beenden"

        if request == stopOption:
            return self.END_REPLY

        return Reply("Hi!", [stopOption])
