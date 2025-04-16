from .repliers import *

from .types import ChatNode

def test_hi_replier():
    replier = HiReplier()

    # Always expect one hi response
    for i in range(1,3):
        request = ChatNode("req", "i", "hi")
        response = replier.reply(request)
        assert len(response) == 1
    
    # Expect no response on "ende"
    request = ChatNode("ende", "i", "ende")
    response = replier.reply(request)
    assert len(response) == 0
