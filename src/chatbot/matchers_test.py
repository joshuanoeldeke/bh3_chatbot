from .matchers import *

def test_matchers():
    matchers = [
        StringMatcher()
    ]
    choices = [
        "Cleanbug",
        "Windowfly",
        "Gardenbeetle",
        "Sonstiges"
    ]
    for matcher in matchers:
        assert "Cleanbug" in matcher.match("Ich habe ein Problem mit meinem Cleanbug", choices)
        assert "Gardenbeetle" in matcher.match("Mein Gardenbeetle funktioniert nicht", choices)
        assert "Sonstiges" not in matcher.match("Keins von allem", choices)
        assert "Sonstiges" in matcher.match("Keins von allem", choices, default = "Sonstiges")
