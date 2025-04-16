import pytest
from unittest.mock import Mock, patch
from prompt_toolkit.document import Document

from .cli import ChatChoiceCompleter, Cli
from .types import ChatNode

@pytest.fixture
def mock_chat():
    chat = Mock()
    chat.current_nodes = [
        ChatNode("n1", "c", "option1;First option"),
        ChatNode("n2", "c", "option2;Second option"),
        ChatNode("n3", "c", "another;Third option")
    ]
    return chat

def test_chat_completer_init(mock_chat):
    """Test that the ChatChoiceCompleter initializes correctly"""
    completer = ChatChoiceCompleter(mock_chat)
    assert completer.chat == mock_chat

def test_chat_completer_empty_input(mock_chat):
    """Test completions with empty input"""
    completer = ChatChoiceCompleter(mock_chat)
    document = Document("")
    
    completions = list(completer.get_completions(document, None))
    
    # All options should be available with empty input
    assert len(completions) == 3
    completion_texts = [c.text for c in completions]
    assert "option1" in completion_texts
    assert "option2" in completion_texts
    assert "another" in completion_texts

def test_chat_completer_partial_match(mock_chat):
    """Test completions with partial input"""
    completer = ChatChoiceCompleter(mock_chat)
    document = Document("opt")
    
    completions = list(completer.get_completions(document, None))
    
    # Only options starting with "opt" should be returned
    assert len(completions) == 2
    completion_texts = [c.text for c in completions]
    assert "option1" in completion_texts
    assert "option2" in completion_texts
    assert "another" not in completion_texts

def test_chat_completer_case_insensitive(mock_chat):
    """Test that completions are case-insensitive"""
    completer = ChatChoiceCompleter(mock_chat)
    document = Document("OPT")
    
    completions = list(completer.get_completions(document, None))
    
    # Should match case-insensitively
    assert len(completions) == 2
    completion_texts = [c.text for c in completions]
    assert "option1" in completion_texts
    assert "option2" in completion_texts

def test_chat_completer_no_match(mock_chat):
    """Test completions with no matches"""
    completer = ChatChoiceCompleter(mock_chat)
    document = Document("xyz")
    
    completions = list(completer.get_completions(document, None))
    
    # Should return no completions
    assert len(completions) == 0

def test_cli_init(mock_chat):
    """Test that Cli initializes correctly"""
    cli = Cli(mock_chat)
    assert isinstance(cli.completer, ChatChoiceCompleter)
    assert cli.completer.chat == mock_chat

@patch('chatbot.cli.prompt')
def test_cli_input(mock_prompt, mock_chat):
    """Test the input method of Cli"""
    mock_prompt.return_value = "test input"
    
    cli = Cli(mock_chat)
    result = cli.input("Enter something: ")
    
    # Check that prompt was called with the right arguments
    mock_prompt.assert_called_once()
    args, kwargs = mock_prompt.call_args
    assert args[0] == "Enter something: "
    assert kwargs["completer"] == cli.completer
    assert kwargs["complete_while_typing"] is True
    
    # Check that the result is what we mocked
    assert result == "test input"