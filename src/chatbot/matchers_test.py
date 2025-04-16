from .matchers import *

from .types import ChatNode

def test_matchers():
    matchers = [
        StringMatcher()
    ]
    nodes = [
        ChatNode('cleanbug', 'c', 'cleanbug;roboter;reinigungsroboter'),
        ChatNode('windowfly', 'c', 'windowfly;fensterroboter'),
        ChatNode('gardenbeetle', 'c', 'gardenbeetle;gartenroboter;unkraut'),
        ChatNode('sonstiges_produkt', 'c', 'sonstiges;anderes'),
    ]
    for matcher in matchers:
        assert isinstance(matcher, Matcher)
        assert matcher.match("Ich habe ein Problem mit meinem Cleanbug", nodes).name == "cleanbug"
        assert matcher.match("Mein Windowfly funktioniert nicht", nodes).name == "windowfly"
        assert matcher.match("Keins von allem", nodes).name != "default"
        assert matcher.match("Keins von allem", nodes, default="sonstiges_produkt").name == "sonstiges_produkt"
