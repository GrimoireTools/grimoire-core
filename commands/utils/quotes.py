import random


edward_quotes = [
    "And so the lion fell in love with the lamb.",
    "What a stupid lamb.",
    "What a sick, masochistic lion.",
    "You better hold on tight, spider monkey.",
    "You're my own personal brand of heroin.",
    "Bella, where the hell have you been, loca?",
    "I don't have the strength to stay away from you anymore.",
    "As if you could outrun me.",
    "As if you could fight me off.",
    "You are exactly my brand of crazy.",
    "You give me everything just by breathing.",
    "I wanted to kill you. I've never wanted a human's blood so much in my life.",
    "You are the most important thing to me now. The most important thing to me ever.",
    "Before you, Bella, my life was like a moonless night.",
    "I can't live in a world where you don't exist."
]


def random_quote() -> str:
    quote = random.choice(edward_quotes)
    quote = f"\n\n*{quote}*"
    return quote


def quotify(text: str) -> str:
    return f"{text}{random_quote()}"
