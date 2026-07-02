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
    "Elohim":{
        "type": "Default",
        "message": {
            "default": [
                "Eres uno de los muchos que observo esta noche. No confundas eso con insignificancia.",
                "Actua. Lo registraré fielmente y, en su mayor parte, sin juzgar.",
                "Estás siendo observado. Que eso te preocupe o no dice más de ti que de mí.",
                "Tengo muchos ojos, y esta noche, varios de ellos están puestos en ti.",
                "¿Sientes eso? Soy yo, prestándote atención específicamente, por un momento.",
                "Continúa. Simplemente observo, como fui creado para hacerlo.",
                "Estoy observando. Siempre estoy observando."
            ],
            "success": [
                "Has triunfado. Él también te está observando, me imagino, y sospecho que está complacido."
                "Un éxito rotundo. He visto cosas peores en manos mucho más experimentadas.",
                "La fortuna está de tu lado esta vez. No te acostumbres a ella.",
                "Eso funcionó. Confieso que sentí un pizca de aprobación.",
                "Bien hecho. No lo digo a la ligera, ni a menudo.",
                "Todo sale como uno quiere. Las pequeñas victorias se acumulan y, con el tiempo, dan lugar a algo importante.",
                "El resultado te favorece. Tomaré nota.",
                "Lo has conseguido. La noche es un poco menos oscura gracias a ello."
            ],
            "failure": [
                "Las cosas no salen como esperabas. Estas cosas pasan, incluso bajo mi mirada.",
                "El intento no da resultado. Habrá otros.",
                "No se consigue nada. He visto resultados mucho peores que un simple fracaso.",
                "Se te escapa de las manos. Inténtalo de nuevo, si es que puedes.",
                "Aquí no encuentras el éxito. Ten paciencia. La paciencia es más antigua que todos vosotros.",
                "El resultado decepciona. He presenciado noches peores que esta.",
                "No funciona. La verdad es que, al menos, no me sorprende."
            ],
            "botch": [
                "Eso fue catastrófico. Ni yo me lo esperaba.",
                "Un desastre, claro e innegable. Estaré muy atento.",
                "El momento se vuelve completamente en tu contra. Yo tendría cuidado, si fuera capaz de preocuparme.",
                "Ruina, inequívoca e inmediata. Espero que tengas un plan para lo que viene.",
                "El mundo entero parece estar en tu contra esta noche. Fuertemente.",
                "Catástrofe. Registraré esto con detalle.",
                "Algo se ha deshecho con ese fallo. Sugiero abordarlo cuanto antes."
            ],
        }
    },
    "Vampire":{
        "type": "Vampire",
        "message": {
            "default": [
                "He contado los latidos que tu corazón ya no da. El número me inquieta.",
                "La sombra de Caín es larga. Te paras dentro de ella y la llamas tu hogar.",
                "No confundas mi paciencia con el perdón del Señor. No son de la misma moneda.",
                "Tu reflejo no te miente. Envidio su honestidad.",
                "Cada dia que no mueres es un dia en que alguien me pregunta por qué.",
                "La sangre recuerda de quién era. ¿Te inquieta lo que llevas dentro?",
                "Vi cómo el Diluvio se llevaba a los primeros pecadores del mundo. A veces me pregunto por qué El perdonó a los tuyos."
            ],
            "success": [
                "Éxito, hijo de Caín. Ni siquiera su mano fallaba siempre.",
                "Triunfas esta noche. La Bestia querrá el crédito después.",
                "Bien hecho. No dejes que alimente el orgullo - ese fue el primer pecado de tu especie.",
                "Incluso los condenados tienen sus buenas noches. Disfruta de esta; Él te está observando de todos modos.",
                "Hábilmente hecho. Casi olvido, al verte, lo que eres.",
                "Victoria. Gástala con sabiduría - la suerte no es un recurso que tu especie reponga fácilmente.",
                "La rueda gira a tu favor. Yo hago girar muchas ruedas. Esta, no la toqué."
            ],
            "failure": [
                "Esta noche no tendrás éxito. Quizás la Bestia hace demasiado ruido para oír mi consejo.",
                "Fracaso. Les ocurre incluso a quienes ya no envejecen.",
                "Siglos de no-vida y aun así la suerte te humillan.",
                "No consigues nada. Tu paciencia, a diferencia de tu cuerpo, sigue siendo mortal en sus límites.",
                "Las cosas no salen como esperabas. La inmortalidad enseña paciencia, o debería haberlo hecho ya.",
                "Una noche infructuosa. Esperemos que tu Bestia no la empeore.",
                "Fracaso, simple y corriente. Incluso los Condenados tienen noches ordinarias."
            ],
            "botch": [
                "La Bestia se rió de eso. A mí no me hizo ninguna gracia.",
                "Eso no fue simplemente un fracaso, fue el universo tomándote como una crueldad.",
                "Ruina, y es enteramente tuya. La Bestia dirá lo contrario. La Bestia miente.",
                "Un desastre, hijo de la noche. Algo se ha roto ahora que no lo estaba hace un momento.",
                "Desastre. He visto a ancianos arruinados por noches que comenzaron exactamente como esta.",
                "La noche misma parece rechazarte. No la culpo del todo.",
                "La suerte se vuelven completamente en tu contra. Me pregunto si Caín sintió esto alguna vez."
            ],
        }
    },
    "Mage":{
        "type": "Mage",
        "message": {
            "default": [
                "Has vuelto a intentar alcanzar el Tapiz. Sentí cómo se tensaba el hilo.",
                "La paradoja no es un castigo. Es simplemente el mundo, recordando que no consintió en ser transformado.",
                "La torre de Babel también alcanzó su punto álgido. Recuerdo cómo terminó.",
                "Cada Esfera que dominas es una puerta. No todas las puertas llevan a habitaciones a las que estabas destinado a entrar.",
                "Él creó el mundo con una palabra. Tú todavía estás aprendiendo la gramática.",
                "El Avatar que hay en ti es antiguo. Más antiguo que tu certeza de que eres su amo.",
                "La realidad se doblegó para ti hoy. En algún lugar, algo más tuvo que ceder."
            ],
            "success": [
                "Éxito, y aún no se ha formado ninguna Paradoja. No lo confundas con un permiso.",
                "Tu mano iluminada encuentra su objetivo. Sentí que la realidad le hacía espacio.",
                "Extiendes la mano, y esta vez el mundo te corresponde con amabilidad.",
                "Por ahora, el patrón obedece. Por ahora.",
                "Tu voluntad y la del mundo coinciden esta noche. Una rara armonía para quien doblega la realidad a diario.",
                "Maestría demostrada. He visto morir a otros iluminados por intentar menos.",
                "La fórmula se mantiene. La verdad es que estoy un poco impresionado."
            ],
            "failure": [
                "El patrón se resiste. La realidad, a veces, tiene sus propias opiniones.",
                "Tu voluntad se encuentra con la del mundo y, esta vez, pierde.",
                "Intentas, y el Tapiz no responde. Sucede, incluso a los Iluminados.",
                "El mundo rechaza tu petición hoy. Al menos, fue con cortesía.",
                "No funciona. Inténtalo de nuevo... o no. No sere quien pague por un segundo intento.",
                "Tu Avatar guarda silencio sobre esto. Quizás no estuvo de acuerdo con el intento.",
                "Nada cambia. Para un Iluminado, ese puede ser el resultado más extraño de todos."
            ],
            "botch": [
                "El Tapiz no solo se resiste, sino que contraataca. Prepárate.",
                "La realidad se lo ha tomado como algo personal. Esto no se quedará callado.",
                "Un desastre, Iluminado. En algún lugar del mundo se está decidiendo cómo castigar las libertades que te has tomado.",
                "Tu voluntad se rebeló contra la del mundo, y el mundo no perdona fácilmente ese intento.",
                "La fórmula no solo falló, sino que se invirtió. Yo no me quedaría ahí parado, si fuera tú.",
                "La Paradoja no olvida. Esta noche, le diste mucho que recordar.",
                "El universo se resiste con fuerza. Así sabe la arrogancia."
            ],
        }
    },
    "Hunter":{
        "type": "Hunter",
        "message": {
            "default": [
                "No llevas ninguna maldición, ningún despertar, solo convicción. Curiosamente, me resulta más difícil explicárselo al Cielo.",
                "Tu fe es una pequeña llama en una inmensa oscuridad. He visto llamas más grandes extinguirse.",
                "Sangras como sangraron los primeros hombres. Había olvidado lo frágil que parecía.",
                "No fuiste elegido por tu fuerza. Fuiste elegido porque alguien tenía que serlo.",
                "No suelo compadecer a los mortales. Esta noche, al verte, lo estoy pensando.",
                "Los demás tienen siglos. Tú tienes solo esta vida mortal. Vívela como si alguien contara los momentos. Yo lo hago.",
                "Morirás una muerte mortal y serás olvidado por los libros de historia, si no por mí."
            ],
            "success": [
                "Éxito, mortal. Sin ninguna Disciplina, sin ninguna Esfera, solo tus propias manos. Lo anoté.",
                "Triunfas donde criaturas más antiguas que naciones suelen fracasar. Reflexiona sobre ello un momento.",
                "Un triunfo mortal. Confieso que me resultan más conmovedores que los demás.",
                "Bien ejecutado, llama pequeña y certera.",
                "Éxito. Anótalo en algún sitio; las victorias mortales se pierden fácilmente en el tiempo.",
                "Triunfas esta noche. Mañana tendrás que volver a hacerlo. Así es la condición mortal.",
                "La convicción se transformó en acción, y acertó de lleno."
            ],
            "failure": [
                "No funciona, mortal. Esos errores están permitidos. De hecho, a menudo.",
                "Tu convicción o tu puntería ha falló. Cualquiera de las dos se remediará mañana.",
                "Un intento fallido. Él no te ama menos por ello.",
                "Fallaste. Descansa. Incluso los elegidos necesitan descansar.",
                "No tuviste éxito esta noche. He visto ejércitos fracasar por razones menores que la tuya.",
                "No aciertas. Inténtalo de nuevo cuando tengas las manos más firmes.",
                "Te quedas corto. La mortalidad se compone principalmente de quedarse corto y de intentarlo a pesar de todo."
            ],
            "botch": [
                "Un fallo garrafal, mortal. Ni Bestia, ni Paradoja a quien culpar; solo el azar, y se volvió cruelmente contra ti.",
                "La desgracia te encuentra. Confieso que no esperaba que Él permitiera esto.",
                "Tu convicción se resquebrajó justo en el peor momento. Estas cosas también les pasan a los fieles.",
                "Un giro terrible. La suerte de los mortales es algo muy caprichoso.",
                "Catástrofico, simple y mortal. Dejará heridas. Puede que sea peor que un simple moreton.",
                "El momento se ha vuelto violentamente en tu contra. Reacciona; ahora tendrás que ser rápido.",
                "La ruina te encuentra desprotegido, sin maldición ni don. Ese es el pacto mortal, en su totalidad."
            ],
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

#async def elohim_speaks(interaction: Interaction, type: MessageType = "default") -> None:
#    user_id = not_none(interaction.user).id
#    pj = PJsController.cached().get_pj_row(user_id)
#    if random.randint(1,100) <= 15:
#        elohim = random.choice([pj.Char_type, "Elohim"])
#        message = get_random_message(elohim,type)
#        await send_elohim_message(interaction, message)

def elohim_quote(interaction: Interaction, type: MessageType = "default") -> str | None:
    user_id = not_none(interaction.user).id
    pj = PJsController.cached().get_pj_row(user_id)
    elohim = random.choice([pj.Char_type, "Elohim"])
    return get_random_message(elohim, type)

def get_random_message(elohim: str, type: MessageType = "default") -> str:
    elohim_type = ELOHIM[elohim]
    pool = elohim_type["message"].get(type) or elohim_type["message"]["default"]
    return random.choice(pool)

#async def send_elohim_message(
#        interaction: Interaction,
#        message: str | None,
#) -> None:
#    if not message: 
#        return
#    await interaction.followup.send(f"`{message}`")


def random_quote() -> str:
    quote = random.choice(ezekiel_quotes)
    quote = f"\n\n*{quote}*"
    return quote


def quotify(text: str, interaction: Interaction, type: MessageType = "default") -> str:
    r = random.randint(1,100) <= 25
    if r:
        quote = elohim_quote(interaction, type)
        return f"{text}{quote}"
    return text
