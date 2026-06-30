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

ezekiel_quotes = [
    "Also out of the midst thereof came the likeness of four living creatures. And this was their appearance: they had the likeness of a man.",
    "And every one had four faces, and every one had four wings.",
    "And their feet were straight feet, and the soles of their feet were like the sole of a calf’s foot; and they sparkled like the color of burnished brass.",
    "And they had the hands of a man under their wings on their four sides; and all four had their faces and their wings.",
    "Their wings were joined one to another. They turned not when they went; they went every one straight forward.",
    "As for the likeness of their faces, all four had the face of a man, and the face of a lion on the right side, and all four had the face of an ox on the left side; they four also had the face of an eagle.",
    "Thus were their faces. And their wings were stretched upward; two wings of every one were joined one to another, and two covered their bodies.",
    "And they went every one straight forward; whither the spirit was to go, they went, and they turned not when they went.",
    "As for the likeness of the living creatures, their appearance was like burning coals of fire and like the appearance of lamps; it went up and down among the living creatures, and the fire was bright, and out of the fire went forth lightning.",
    "And the living creatures ran and returned, like the appearance of a flash of lightning."
]


def random_quote() -> str:
    quote = random.choice(ezekiel_quotes)
    quote = f"\n\n*{quote}*"
    return quote


def quotify(text: str) -> str:
    r = random.choice([True, False])
    if r:
        return f"{text}{random_quote()}"
    return text
