from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion

# Completer that accesses live chat data
class ChatChoiceCompleter(Completer):
    def __init__(self, chat):
        self.chat = chat

    def get_completions(self, document, complete_event):
        word = document.text_before_cursor
        for choice in self.chat.last_reply.choices:
            if choice.lower().startswith(word.lower()):
                yield Completion(choice, start_position=-len(word))

class Cli:
    def __init__(self, chat) -> None:
        self.completer = ChatChoiceCompleter(chat)

    def input(self, msg: str) -> str:
        return prompt(msg, completer = self.completer, complete_while_typing = True)
