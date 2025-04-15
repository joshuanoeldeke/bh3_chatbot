import chatbot

from chatbot import ChatNode

# Defining a simple test graph
chatGraph = ChatNode("start", "o", "Guten Morgen!")
stimmung_fragen = chatGraph.addChild(ChatNode("stimmung_fragen", "o", "Wie geht es dir?"))

stimmung_gut = stimmung_fragen.addChild(ChatNode("stimmung_gut", "c", "Gut"))
stimmung_schlecht = stimmung_fragen.addChild(ChatNode("stimmung_schlecht", "c", "Schlecht"))
stimmung_neutral = stimmung_fragen.addChild(ChatNode("stimmung_neutral", "c", "Neutral"))

stimmung_antwort = ChatNode("stimmung_antwort", "o", "Das ist schön zu hören!")
stimmung_gut.addChild(stimmung_antwort)
stimmung_schlecht.addChild(stimmung_antwort)
stimmung_neutral.addChild(stimmung_antwort)

# Let's use the graph for our chatbot
replier = chatbot.repliers.GraphReplier(chatGraph)
matcher = chatbot.matchers.StringMatcher()
chat = chatbot.chat.Chat(replier, matcher)

# Helper CLI that adds tab-completion to reply choices provided by the chatbot
chat_cli = chatbot.Cli(chat)

request = chat.START

while (nodes := chat.advance(request)):
    match nodes[0].type:
        case "o":
            print(f"Chatbot: {nodes[0].content}")
        case _:
            request = chat_cli.input("You: ")
