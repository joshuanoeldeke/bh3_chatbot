import chatbot

replier = chatbot.repliers.HiReplier()
matcher = chatbot.matchers.StringMatcher()
chat = chatbot.chat.Chat(replier, matcher)

# Helper CLI that adds tab-completion to reply choices provided by the chatbot
chat_cli = chatbot.Cli(chat)

request = chat.START

while (response := chat.advance(request)):
    print(f"Chatbot: {response}")

    if response == chat.END:
        break

    request = chat_cli.input("You: ")
