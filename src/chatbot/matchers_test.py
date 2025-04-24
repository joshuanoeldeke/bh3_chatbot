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

def test_semantic_match_fallback_to_match():
    """Test that semantic_match falls back to match when no model is available"""
    matcher = StringMatcher()
    nodes = [ChatNode('x','c','foo'), ChatNode('y','c','bar')]
    # With no model loaded, semantic_match should behave like match
    result = matcher.semantic_match('I want foo', nodes, default='y')
    assert result.name == 'x'
    # Default fallback
    result_default = matcher.semantic_match('no match here', nodes, default='y')
    assert result_default.name == 'y'

def test_semantic_log_records_exact_match():
    """Test that semantic_match logs exact keyword matches"""
    matcher = StringMatcher()
    nodes = [ChatNode('n1','c','hello;hi'), ChatNode('n2','c','bye;goodbye')]
    # Perform an exact match
    _ = matcher.semantic_match('Well, hello there', nodes)
    assert hasattr(matcher, 'semantic_log')
    assert matcher.semantic_log, 'semantic_log should not be empty'
    request_log, node_name, detail = matcher.semantic_log[-1]
    assert request_log == 'Well, hello there'
    assert node_name == 'n1'
    assert 'exact' in detail
