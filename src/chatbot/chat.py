from .repliers import *
from .matchers import *

class Chat:
    def __init__(self, replier: Replier, matcher: Matcher):
        self.replier = replier
        self.matcher = matcher
        self.choices = []
        
        self.START = ""
        self.END = replier.END_REPLY

    def advance(self, request: str) -> Reply:
        closestChoice = self.matcher.match(request, self.choices)
        reply = self.replier.reply(closestChoice)

        self.choices = reply.choices
        return reply
