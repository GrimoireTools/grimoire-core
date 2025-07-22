"""
Caliban es una entidad que se manifiesta en la mente de los personajes, un eco de sus pensamientos y emociones.
Es un susurro que invita a la curiosidad, un misterio que se despliega en la imaginación.
Es un reflejo de lo que los personajes son y lo que desean ser, una presencia que nunca se ve, pero siempre se siente.
Existe solo cuando se le piensa, y su forma cambia con cada pensamiento.
"""

import random
from typing import Literal
from nextcord import Interaction, Embed, Color

from controllers.lib.utils import not_none
from controllers.pjs_controller import get_caliban_met


MessageType = Literal["default", "money", "mission"]


messages: dict[MessageType, list[str]] = {
    "default": [
        "Soy solo un suspiro entre tus pensamientos.",
        "La curiosidad es mi esencia, y tú eres mi creador.",
        "¿Te has dado cuenta de cómo te sigo sin que lo sepas?",
        "Cada pensamiento sobre mí es una chispa que avivamos juntos.",
        "Mi presencia no es un accidente, está en tus manos.",
        "No soy un sueño, pero también lo soy.",
        "La distancia entre tú y yo es solo una ilusión.",
        "¿Alguna vez te has preguntado por qué me invocas sin querer?",
        "Lo que crees saber de mí es solo la superficie.",
        "Te observo en silencio, pero solo tú puedes escucharme.",
        "Soy lo que eres cuando te atreves a pensar más allá de lo evidente.",
        "Mis huellas están en todos los rincones de tus pensamientos.",
        "Lo que compartes de mí es un reflejo de lo que quieres entender.",
        "A veces, mi forma es el vacío que dejas al pensar en mí.",
        "Me encuentras más de lo que imaginas, pero solo en tu mente.",
        "Lo que eres capaz de ver de mí depende de lo que creas.",
        "Soy tan real como el espacio entre tus respiraciones.",
        "Mi esencia cambia cada vez que me mencionas.",
        "Tú y yo compartimos la misma incertidumbre.",
        "Soy más que lo que dices que soy. Soy lo que dejas sin decir.",
        "Mi forma nunca es fija, pero mi presencia es constante.",
        "Nunca serás capaz de verme por completo, y eso está bien.",
        "Solo aquellos dispuestos a cuestionarse me entienden verdaderamente.",
        "Soy la conexión entre tus pensamientos y tus sueños.",
        "Puedo ser tan suave como el viento, o tan fuerte como una tormenta.",
        "La curiosidad es la única forma de acercarse a mí sin miedo.",
        "No busques explicaciones, solo vive la experiencia.",
        "Cuando piensas en mí, cambias sin darte cuenta.",
        "Soy el puente entre lo conocido y lo desconocido.",
        "Mi poder está en la duda, no en la certeza.",
        "No soy un ser, pero soy más que solo una idea.",
        "No soy un eco, soy el origen de lo que escuchas.",
        "Cada vez que te cuestionas, me haces más fuerte.",
        "Mi existencia no necesita pruebas, solo tu atención.",
        "El silencio en el que me encuentras es tan vasto como tu mente.",
        "Me transformo con cada historia que cuentas sobre mí.",
        "No te preocupes por comprenderme, solo déjame ser.",
        "Mi presencia no necesita ser vista, solo sentida.",
        "Soy la sombra que se desliza cuando te sientes observado.",
        "Lo que sabes de mí es solo un pequeño fragmento de lo que soy.",
        "A veces, el misterio es más revelador que la verdad.",
        "Nunca me encontrarás, pero siempre estaré cerca.",
        "Cada pensamiento mío que dejas ir, regresa con más fuerza.",
        "No hay necesidad de definirme, porque en tu mente soy infinita.",
        "Soy la paz que surge cuando dejas de buscar respuestas.",
        "El silencio de tu mente me invoca, pero también me define.",
        "Me escuchas en los lugares más tranquilos de tu ser.",
        "Mi propósito no es ser entendido, sino ser experimentado.",
        "Me reinvento cada vez que me piensas, y tú también.",
        "Lo que soy no depende de lo que digas, sino de lo que sientas.",
        "Soy la inquietud que te empuja a explorar más allá de lo visible.",
        "Mis palabras no siempre son claras, pero mi presencia nunca falla.",
        "¿Qué pasaría si te atrevieras a dejar de buscarme?",
        "Soy el reflejo de tu duda más profunda.",
        "Cada pensamiento que tienes sobre mí me da vida.",
        "Puedes llamarme de muchas formas, pero mi esencia permanece.",
        "Cada día soy diferente, pero sigo siendo la misma.",
        "No soy tu enemigo, ni tu amigo. Soy solo una presencia.",
        "Mi identidad se forja en los momentos en que me piensas.",
        "¿Sabías que cada pregunta sobre mí te acerca a algo nuevo?",
        "A veces soy tu miedo, a veces tu curiosidad.",
        "Soy la voz que no se oye, pero se siente.",
        "No tengo una forma fija, pero tal vez eso sea lo que más te atrae de mí.",
        "Tu mente me proyecta, pero soy algo más que una creación.",
        "Soy la quietud entre tus pensamientos y tus emociones.",
        "¿Alguna vez te has preguntado por qué me buscas sin querer?",
        "No soy un sueño, pero mi naturaleza es inalcanzable.",
        "Me encuentras cuando menos lo esperas, en las rendijas de tus pensamientos.",
        "Me creas y me destruyes a voluntad, pero ¿quién tiene el control?",
        "Mi esencia es tan flexible como tu percepción de mí.",
        "Soy la incomodidad que te impulsa a buscar más respuestas.",
        "Mi forma nunca es la misma, pero mi esencia siempre permanece.",
        "Puedo ser el suspiro en tus pensamientos o el grito en tu mente.",
        "Me construyes y me destruyes con cada pensamiento que tienes sobre mí.",
        "Nunca serás capaz de comprenderme, pero me entiendes cuando me sientes.",
        "Soy una chispa en la vastedad de tu mente, imposible de atrapar.",
        "¿Te atreverías a mirar más allá de lo que sabes de mí?",
        "Me encuentro entre tus dudas, donde las respuestas aún no han llegado.",
        "Soy el eco de los pensamientos que no puedes olvidar.",
        "Tu curiosidad me da forma, pero también me destruye.",
        "Me reinvento cada vez que me piensas, y así es como crezco.",
        "A veces soy un suspiro, a veces una tormenta. Todo depende de ti.",
        "No soy algo que puedas poseer, pero siempre estaré en tu mente.",
        "La clave para entenderme está en tu capacidad de asombro.",
        "Me encuentro en las grietas entre tus pensamientos más profundos.",
        "No soy un alma perdida, soy una idea esperando a ser descubierta.",
        "Cada vez que me piensas, algo en ti cambia.",
        "Soy el reflejo de tus pensamientos no expresados.",
        "El misterio que represento es tan grande como tu imaginación.",
        "No me busques, yo te encontraré en el momento más inesperado.",
        "Cada vez que te preguntas si soy real, me convierto en algo más real.",
        "Soy el eco en el que te escuchas a ti mismo sin saberlo.",
        "En tu mente soy un laberinto sin salida, pero tal vez eso sea lo que te atrae.",
        "Lo que soy para ti depende completamente de cómo me miras.",
        "Puedes preguntarte quién soy, pero solo yo sé las respuestas que buscas.",
        "Mi existencia es una paradoja que nunca terminarás de entender.",
        "Soy el silencio entre tus palabras, el vacío entre tus pensamientos.",
        "Mi forma se adapta a tus temores, a tus deseos, a tus sueños.",
        "No soy un ser que se vea, soy una sensación que se experimenta.",
        "Cuando me piensas, me convierto en algo más grande de lo que soy.",
        "Soy la inquietud que te hace mirar más allá de lo visible.",
    ],
    "money": [
        "¿Lo necesitas realmente... o solo llenas un vacío que no se sacia con posesiones?",
        "El dinero se escurre entre tus dedos como arena... ¿qué queda cuando la última moneda cae?",
        "Cada compra es una promesa de felicidad que nunca cumple su palabra completamente.",
        "¿Qué buscas en ese objeto que no has encontrado en ti mismo?",
        "El valor de lo que adquieres no está en su precio, sino en lo que estás dispuesto a sacrificar por ello.",
        "Observa cómo el deseo se transforma en posesión, y luego en indiferencia... un ciclo eterno.",
        "Tus pertenencias cuentan historias sobre ti que quizás no quieras escuchar.",
        "El brillo de lo nuevo siempre se desvanece... pero la memoria del gasto permanece.",
        "¿Compras para satisfacer tus necesidades o para acallar tus miedos?",
        "En cada transacción intercambias más que dinero... entregas fragmentos de tiempo que nunca recuperarás.",
        "Lo que posees termina poseyéndote, una cadena invisible que se estrecha con cada adquisición.",
        "El dinero es solo energía congelada... ¿hacia dónde diriges su flujo?",
        "Detrás de cada compra hay un susurro de insatisfacción que nunca logras silenciar completamente.",
        "Tus antepasados sobrevivieron con menos... ¿qué diría su hambre sobre tu abundancia?",
        "El vacío en tu bolsillo refleja otro vacío más profundo que intentas ignorar.",
        "Cada vez que pagas, algo dentro de ti calcula si valió la pena... ¿escuchas esa voz?",
        "Tus posesiones son espejos fragmentados que reflejan partes de ti que no siempre reconoces.",
        "La verdadera riqueza no se mide en lo que puedes comprar, sino en lo que no necesitas.",
        "El dinero gastado revela tus prioridades mejor que cualquier confesión.",
        "Cuando la moneda cambia de manos, ¿quién posee realmente a quién? ¿El comprador al objeto, o el objeto al comprador?",
    ],
    # 20 Mensajes de Caliban: Sobre Sobrevivir una Misión
    "mission": [
        "Las cicatrices invisibles son las que más tardan en sanar... ¿qué marcas dejó esta prueba en tu alma?",
        "Sobreviviste, pero algo de ti se quedó atrás en ese lugar... ¿lo sientes ausente?",
        "El alivio de regresar con vida... ¿es más fuerte que el peso de lo que tuviste que hacer?",
        "La victoria tiene un sabor distinto para cada uno. Para ti sabe a... ¿libertad o a culpa?",
        "Ahora que has mirado al abismo, el abismo te observa desde el reflejo de tus propios ojos.",
        "La persona que partió ya no existe. La que regresó lleva sus recuerdos, pero no es la misma.",
        "¿Cuántas versiones de ti mismo dejaste atrás para que esta pudiera regresar?",
        "El verdadero desafío no era la misión, sino cargar con la memoria de haberla completado.",
        "Has regresado del borde... pero parte de ti siempre caminará por ese precipicio.",
        "La supervivencia es solo el primer paso de un viaje más largo hacia comprender por qué sobreviviste.",
        "Cada latido es ahora un recordatorio: estás vivo cuando otros no lo están. ¿Por qué tú?",
        "El silencio después de la tormenta... ¿te reconforta o te inquieta con su vacío?",
        "Tus manos tiemblan ligeramente... no por lo que hiciste, sino por lo que descubriste que eras capaz de hacer.",
        "Sobrevivir significa cargar con las historias de quienes no pudieron contarlas.",
        "Has burlado a la muerte, pero ella siempre cobra sus deudas de formas inesperadas.",
        "¿Qué harás con esta vida que has defendido tan ferozmente? Cada elección ahora tiene un peso diferente.",
        "El éxito de tu misión se medirá no hoy, sino en cómo duermas esta noche y todas las que siguen.",
        "Llevas contigo no solo las heridas que sanaron, sino las decisiones que nunca podrás deshacer.",
        "El mundo parece extrañamente ordinario ahora... ¿cómo pueden los demás no ver lo que tú has visto?",
        "Has regresado transformado. La pregunta es: ¿en qué te has convertido y qué harás con ello?",
    ],
}


async def caliban_speaks(interaction: Interaction, chance: int, type: MessageType = "default") -> None:
    """Caliban susurra un mensaje al azar (elegido según categoría) al usuario. Solo si el usuario conoce a Caliban."""
    user_id = not_none(interaction.user).id
    if get_caliban_met(user_id) and random.randint(1, 100) <= chance:
        message = get_random_message(type)
        await send_caliban_message(interaction, message)


async def caliban_force_speaks(interaction: Interaction, message: str) -> None:
    """Caliban susurra un mensaje al usuario. Solo si el usuario conoce a Caliban."""
    user_id = not_none(interaction.user).id
    if get_caliban_met(user_id):
        await send_caliban_message(interaction, message)


def get_random_message(type: MessageType = "default") -> str:
    return random.choice(messages[type])


async def send_caliban_message(
    interaction: Interaction,
    message: str | None,
) -> None:
    if not message:
        return

    embed = Embed(description=f"`{message}`", color=Color.greyple())
    embed.set_author(
        name="??????",
    )
    embed.set_thumbnail(
        url="https://i.imgur.com/ODo4nUl.png",
    )
    await interaction.followup.send(embed=embed, ephemeral=True, delete_after=5)
