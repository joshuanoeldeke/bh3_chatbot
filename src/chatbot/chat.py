from .repliers import *
from .matchers import *

class Chat:
    def __init__(self, replier: Replier, matcher: Matcher):
        self.replier = replier
        self.matcher = matcher
        self.last_reply = EmptyReply()
        
        self.START = ""
        self.END = replier.END_REPLY

    def advance(self, request: str) -> Reply:
        closestChoice = self.matcher.match(request, self.last_reply.choices)
        self.last_reply = self.replier.reply(closestChoice)
        return self.last_reply
