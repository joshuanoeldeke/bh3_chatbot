import pytest
from unittest.mock import Mock
from .chat import Chat
from .types import ChatNode

@pytest.fixture
def mock_replier():
    replier = Mock()
    start_nodes = [ChatNode("start", "o", "Welcome!")]
    replier.get_start.return_value = start_nodes
    return replier

@pytest.fixture
def mock_matcher():
    return Mock()

@pytest.fixture
def chat(mock_replier, mock_matcher):
    return Chat(mock_replier, mock_matcher)

def test_initialization(chat, mock_replier, mock_matcher):
    """Test that Chat initializes correctly"""
    assert chat.replier == mock_replier
    assert chat.matcher == mock_matcher
    assert chat.current_nodes == mock_replier.get_start()
    assert chat.START == ""

def test_advance_with_regular_node(chat, mock_matcher, mock_replier):
    """Test advancing conversation with a regular node"""
    # Set up the test scenario
    request = "hello"
    matched_node = ChatNode("greeting", "o", "Hi there!")
    next_nodes = [ChatNode("options", "c", "What would you like to do?")]
    
    # Capture the current nodes before the test
    current_nodes = chat.current_nodes
    
    # Configure the mocks
    mock_matcher.semantic_match.return_value = matched_node
    mock_replier.reply.return_value = next_nodes
    
    # Call the method under test
    result = chat.advance(request)
    
    # Verify the behavior using captured nodes
    mock_matcher.semantic_match.assert_called_once_with(request, current_nodes, default=chat.START)
    mock_replier.reply.assert_called_once_with(matched_node)
    assert result == next_nodes
    assert chat.current_nodes == next_nodes
    assert matched_node.content == "Hi there!"

def test_advance_with_input_node(chat, mock_matcher, mock_replier):
    """Test advancing conversation with an input node"""
    # Set up the test scenario
    request = "my name is Alice"
    matched_node = ChatNode("name_input", "i", "")  # Empty content for input node
    next_nodes = [ChatNode("greeting", "o", "Nice to meet you, Alice!")]
    
    # Configure the mocks
    mock_matcher.semantic_match.return_value = matched_node
    mock_replier.reply.return_value = next_nodes
    
    # Call the method under test
    result = chat.advance(request)
    
    # Verify the behavior
    assert matched_node.content == request  # Content should be updated
    assert result == next_nodes
    assert chat.current_nodes == next_nodes

def test_conversation_flow(chat, mock_matcher, mock_replier):
    """Test a multi-step conversation flow"""
    # First request
    first_request = "hello"
    first_matched = ChatNode("greeting", "o", "Hi there!")
    first_response = [ChatNode("question", "o", "How are you?")]
    
    mock_matcher.semantic_match.return_value = first_matched
    mock_replier.reply.return_value = first_response
    
    result1 = chat.advance(first_request)
    assert result1 == first_response
    assert chat.current_nodes == first_response
    
    # Second request
    second_request = "I'm good"
    second_matched = ChatNode("feeling", "i", "")
    second_response = [ChatNode("farewell", "o", "Glad to hear that!")]
    
    mock_matcher.semantic_match.return_value = second_matched
    mock_replier.reply.return_value = second_response
    
    result2 = chat.advance(second_request)
    assert second_matched.content == second_request
    assert result2 == second_response
    assert chat.current_nodes == second_response

def test_advance_fallback_to_match(chat):
    """Test that advance falls back to match when semantic_match is unavailable"""
    # Create a matcher with only match method
    class OnlyMatchMatcher:
        def match(self, request, nodes, default=""):
            return nodes[0]
    # Override chat matcher and replier
    chat.matcher = OnlyMatchMatcher()
    node = ChatNode("n", "o", "content")
    chat.current_nodes = [node]
    chat.replier.reply = lambda req: [node]

    result = chat.advance("anything")
    assert result == [node]
    assert chat.log[-1] is node


def test_chat_log_accumulates(chat, mock_matcher, mock_replier):
    """Test that chat.log accumulates all matched nodes"""
    first_node = ChatNode("first", "o", "First")
    second_node = ChatNode("second", "o", "Second")
    mock_matcher.semantic_match.return_value = first_node
    mock_replier.reply.return_value = [first_node]
    chat.advance("one")
    mock_matcher.semantic_match.return_value = second_node
    mock_replier.reply.return_value = [second_node]
    chat.advance("two")
    assert chat.log == [first_node, second_node]