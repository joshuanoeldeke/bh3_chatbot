import chatbot

replier = chatbot.repliers.HiReplier()
matcher = chatbot.matchers.StringMatcher()
chat = chatbot.chat.Chat(replier, matcher)

request = chat.START

while (response := chat.advance(request)):
    print(f"Chatbot: {response}")

    if response == chat.END:
        break

    request = input("You: ")
