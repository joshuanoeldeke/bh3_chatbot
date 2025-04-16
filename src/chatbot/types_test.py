from .types import *

def test_reply_eq():
    reply = Reply("Schönen Tag noch!", ["Danke"])
    reply2 = Reply("Test", [])
    reply3 = Reply("Schönen Tag noch!", [])

    assert reply == reply
    assert reply != reply2
    assert reply == reply3
