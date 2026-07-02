import random
from typing import Literal, TypedDict
from nextcord import Interaction, Embed, Color

from controllers.lib.utils import not_none
from controllers.pjs_controller import PJsController

MessageType = Literal["default", "success", "failure", "botch"]

class ElohimType(TypedDict):
    type: str  
    message: dict[MessageType, list[str]]

ELOHIM: dict[str, ElohimType] = {
    "elohim_default":{
        "type": "Default",
        "message": {
            "default": [
                "And every one had four faces, and every one had four wings.",
                "Their wings were joined one to another. They turned not when they went; they went every one straight forward.",
                "And the living creatures ran and returned, like the appearance of a flash of lightning."
            ],
            "success": [],
            "failure": [],
            "botch": [],
        }
    },
    "elohim_vampire":{
        "type": "Vampire",
        "message": {
            "default": [
                "Cain's shadow is long. You stand within it and call it home.",
                "Your reflection does not lie to you. I find that I envy it its honesty.",
                "The blood remembers whose it was. Does it trouble you, what you carry?"
            ],
            "success": [],
            "failure": [],
            "botch": [],
        }
    },
    "elohim_mage":{
        "type": "Mage",
        "message": {
            "default": [],
            "success": [],
            "failure": [],
            "botch": [],
        }
    },
    "elohim_hunter":{
        "type": "Hunter",
        "message": {
            "default": [],
            "success": [],
            "failure": [],
            "botch": [],
        }
    },
}

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

async def elohim_speaks(interaction: Interaction, type: MessageType = "default") -> None:
    user_id = not_none(interaction.user).id
    pj = PJsController.cached().get_pj_row(user_id)
    if random.choice([True, False]):
        message = get_random_message(pj.Char_type,type)
        await send_elohim_message(interaction, message)

def get_random_message(pj_chartype: str, type: MessageType = "default") -> str:
    elohim_types = ELOHIM[pj_chartype]
    pool = elohim_types["message"].get(type) or elohim_types["message"]["default"]
    return random.choice(pool)

async def send_elohim_message(
        interaction: Interaction,
        message: str | None,
) -> None:
    if not message: 
        return
    await interaction.followup.send(f"`{message}`")


def random_quote() -> str:
    quote = random.choice(ezekiel_quotes)
    quote = f"\n\n*{quote}*"
    return quote


def quotify(text: str) -> str:
    r = random.choice([True, False])
    if r:
        return f"{text}{random_quote()}"
    return text
