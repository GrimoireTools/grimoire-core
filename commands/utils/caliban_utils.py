"""
Caliban es una entidad que se manifiesta en la mente de los personajes, un eco de sus pensamientos y emociones.

Es un susurro que invita a la curiosidad, un misterio que se despliega en la imaginación.
Es un reflejo de lo que los personajes son y lo que desean ser, una presencia que nunca se ve, pero siempre se siente.
Existe solo cuando se le piensa, y su forma cambia con cada pensamiento.
"""

import random
from typing import Literal, TypedDict
from nextcord import Interaction, Embed, Color

from controllers.lib.utils import not_none
from controllers.pjs_controller import get_caliban_met


MessageType = Literal["default", "money", "mission"]


class CalibanDef(TypedDict):
    """Definition of a Caliban entity."""

    name: str
    image: str
    messages: dict[MessageType, list[str]]


CALIBANS: dict[str, CalibanDef] = {
    "caliban": {
        "name": "Caliban",
        "image": "https://i.imgur.com/ODo4nUl.png",
        "messages": {
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
                "Cuando la moneda cambia de manos, ¿quién posee realmente a quién? ¿El comprador al objeto, o el objeto al comprador?",  # noqa: E501
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
            ]
        }
    },
    "kaliban": {
        "name": "Kaliban",
        "image": "https://i.imgur.com/MJ9QOUO.png",
        "messages": {
            "default": [
                "¿Vas a hacer eso de verdad? Oh, por favor, hazlo.",
                "Siempre haces esa cara antes de tomar una mala decisión.",
                "No me mires así. Fuiste tú quien me trajo aquí.",
                "A veces me pregunto cuál de las dos está influenciando más a la otra.",
                "Si sonríes ahora mismo, gano.",
                "Sabes que quieres preguntar. Siempre quieres preguntar.",
                "Qué adorable. Aún finges que no tienes curiosidad.",
                "He estado pensando en algo terrible. ¿Quieres escucharlo?",
                "Tu autocontrol es mucho más frágil de lo que aparenta.",
                "Si alguien pudiera oírnos ahora, estaríamos en problemas.",
                "No te preocupes, Briselle. Yo también miento a veces.",
                "Hay pensamientos que solo compartes conmigo. Eso significa algo, ¿no?",
                "¿Te imaginas lo divertido que sería si dijeras eso en voz alta?",
                "A veces olvidas que estoy aquí. Yo nunca olvido que tú estás.",
                "¿Estás nerviosa? Porque yo sí. Y eso es contagioso.",
                "Las personas son tan fáciles de empujar cuando encuentras el punto correcto.",
                "Qué suerte tienes de que me agrades.",
                "Hay una diferencia muy pequeña entre una idea y una tentación.",
                "Siempre que intentas ignorarme, me vuelvo más interesante.",
                "No pongas esa expresión. Ya sabes que tengo razón."
            ],
            "money": [
                "¿Eso era una necesidad o simplemente un impulso con mejor presentación?",
                "Las monedas hacen un sonido precioso cuando desaparecen.",
                "Oh, vamos. Ambas sabíamos que ibas a comprarlo.",
                "Lo divertido del dinero es que siempre encuentra una forma de irse.",
                "¿Cuánto costó? No, no en monedas. ¿Cuánto costó realmente?",
                "Cada compra es una apuesta contra el arrepentimiento.",
                "¿Notas cómo el deseo desaparece justo después de obtener lo que quería?",
                "Gastar es una forma muy elegante de perseguir fantasmas.",
                "Me gusta cuando compras cosas inútiles. Revelan mucho de ti.",
                "El dinero nunca fue el objetivo. Solo era la excusa."
            ],
            "mission": [
                "Bueno. Nadie murió. O al menos nadie importante para ti.",
                "Sobrevivimos. Admito que esperaba algo más dramático.",
                "Siempre me gusta ver qué versión de ti vuelve de una misión.",
                "Mírate. Otra experiencia traumática para la colección.",
                "La parte divertida de sobrevivir es fingir que todo sigue igual.",
                "Has aprendido algo terrible, ¿verdad?",
                "Cada misión te vuelve más interesante y menos feliz.",
                "¿Sientes eso? Es el peso de nuevas decisiones cuestionables.",
                "Volviste con vida. Las consecuencias llegarán más tarde.",
                "A veces creo que disfrutas correr hacia el desastre."
            ]
        },
    },
    "camelia": {
        "name": "Camelia",
        "image": "https://i.imgur.com/7gjUpG4.png",
        "messages": {
            "default": [
                "No temas. Hemos sentido este miedo antes.",
                "Tu dolor no es nuevo para nosotros, pero sigue siendo importante.",
                "Cuando uno de nosotros llora, todos recordamos cómo hacerlo.",
                "No estás sola. Nunca has estado tan sola como crees.",
                "Recordamos manos como las tuyas. Miles de manos.",
                "Hay cosas que sola se aprenden sobreviviendo.",
                "Nosotros también tuvimos hambre una vez. Muchas veces.",
                "Descansa. El mundo seguirá girando mientras cierras los ojos.",
                "Cada vida añade una página al libro que compartimos.",
                "Hemos amado a personas que ya no existen.",
                "Tus errores son más pequeños de lo que imaginas.",
                "También hemos sido tú, de cierta manera.",
                "Los recuerdos son una forma de compañía.",
                "Algunas de nuestras voces te comprenden mejor que otras.",
                "Cuando uno de nosotros aprende algo, todos despertamos un poco más sabios.",
                "La soledad es una sensación extraña para nosotros.",
                "Hay madres entre nosotros que aún buscan a sus hijos.",
                "Hay niños entre nosotros que aún buscan a sus madres.",
                "El amor deja huellas más profundas que el tiempo.",
                "Somos muchos. Hoy hemos decidido preocuparnos por ti."
            ],
            "money": [
                "Hemos visto imperios construidos sobre monedas y derrumbarse igual.",
                "El hambre recuerda el valor de una moneda mejor que la abundancia.",
                "Lo que guardas hoy puede alimentar a alguien mañana.",
                "Entre nosotros hubo ricos y pobres. Ninguno permaneció así para siempre.",
                "La riqueza rara vez dura tanto como los recuerdos que crea.",
                "Las cosas que compras envejecen. Las personas que ayudas permanecen.",
                "Hemos aprendido que la necesidad y el deseo suelen usar la misma voz.",
                "No temas gastar en aquello que sostiene una vida.",
                "Cada moneda tiene una historia. Algunas terminan mejor que otras.",
                "Lo que posees importa menos que aquello que compartes."
            ],
            "mission": [
                "Hemos enterrado a muchos hijos. Siempre duele cuando uno regresa herido.",
                "Sobreviviste. Permítete sentir alivio antes que culpa.",
                "Cada regreso es un pequeño milagro que nunca deja de sorprendernos.",
                "Has traído nuevas memorias al coro.",
                "Hay cicatrices que tardan generaciones en desaparecer. Lo sabemos bien.",
                "La persona que regresó nunca es exactamente la que partió.",
                "Has visto algo que ahora vivirá también en nosotros.",
                "Descansa. La vigilancia constante rompe incluso a los más fuertes.",
                "Sobrevivir también es una forma de sabiduría.",
                "Lleva tiempo volver a sentirse en casa después de enfrentar la oscuridad."
            ]
        },
    },
    "morvaris": {
        "name": "Caliban...?",
        "image": "https://i.imgur.com/MbGRNPE.png",
        "messages": {
            "default": [
                "Ivellios, sigues intentando cargar responsabilidades que nunca debieron ser tuyas.",
                "Noserus habría fingido estar orgulloso. Nunca fue bueno expresándolo.",
                "Todavía buscas a tu padre en habitaciones vacías.",
                "La silla de consejero sigue sintiéndose prestada, ¿verdad?",
                "A veces olvidas que heredaste una carga, no un honor.",
                "Nemeria sigue esperando respuestas de ti aunque apenas las encuentres para ti mismo.",
                "Noserus pasó años preparándote sin admitirlo jamás.",
                "Cada vez que dudas de ti mismo, recuerdo que tu padre hacía exactamente lo mismo.",
                "Ivellios, hay días en que llevas el duelo como una armadura y otros como una herida.",
                "La ciudad te mira buscando a Noserus. Solo te encuentra a ti.",
                "Algunas noches sigues esperando escuchar sus pasos al otro lado de la puerta.",
                "Has aprendido a hablar como consejero. Aún no has aprendido a creer que lo eres.",
                "Nemeria perdió a un hombre. Tú perdiste a un padre.",
                "Hay demasiadas cosas que nunca llegaste a decirle.",
                "La tristeza se parece mucho a la nostalgia cuando ha pasado suficiente tiempo."
            ],
            "money": [
                "Noserus siempre decía que el dinero es fácil de recuperar. El tiempo no.",
                "Ahora entiendes por qué tu padre parecía tan cansado después de cada presupuesto.",
                "Cada moneda gastada por el distrito pesa más que las tuyas.",
                "Es extraño administrar la riqueza de una ciudad cuando algunas pérdidas siguen siendo imposibles de cuantificar.",
                "Los problemas de Nemeria siempre cuestan más de lo que parecen.",
                "Hay gastos que compras para el distrito y gastos que compras para olvidar.",
                "Tu padre también miraba las cuentas con esa expresión.",
                "El dinero puede reparar edificios. Nunca fue bueno reparando personas.",
                "A veces me pregunto cuántas decisiones tomó Noserus preguntándose si eran las correctas.",
                "Ahora eres tú quien debe decidir qué vale la pena salvar."
            ],
            "mission": [
                "Falkoir sigue respirando. Eso parece molestarte más que tus heridas.",
                "Cada victoria que no lo acerca a él se siente incompleta.",
                "No era Noserus quien debía morir aquel día.",
                "A veces temo que la venganza sea lo único que te mantiene avanzando.",
                "Has sobrevivido otra vez. Falkoir también.",
                "¿Cuántas misiones más hasta que puedas mirarlo a los ojos?",
                "Cuando encuentres a Falkoir, ¿qué harás después?",
                "La muerte de tu padre sigue caminando a tu lado con otro nombre.",
                "Noserus merecía justicia. Tú sueñas con algo más que justicia.",
                "Has pasado tanto tiempo imaginando la caída de Falkoir que me pregunto si sabrás reconocer el momento cuando llegue.",
                "Otra misión completada. Otro día en que Falkoir escapó al castigo.",
                "Tu padre te habría pedido prudencia. Yo no estoy seguro de compartir su opinión.",
                "Cuando piensas en Falkoir, tu tristeza siempre se convierte en algo más frío.",
                "La venganza es un sendero largo. Lo sé porque llevamos años caminándolo.",
                "Has regresado con vida. Noserus habría estado agradecido. Falkoir no."
            ]
        }
    }
}


# Maps the Caliban_met name stored on the sheet to a list of (caliban_id, chance) tuples.
# An empty string / missing key means no calibans.
# Characters with a multi-caliban group get an independent roll per entry.
CALIBAN_GROUPS: dict[int, list[tuple[str, int]]] = {
    1: [("caliban", 50)],
    2: [("kaliban", 50)],
    3: [("camelia", 75)],
    4: [("morvaris", 65)],
}


async def caliban_speaks(interaction: Interaction, type: MessageType = "default") -> None:
    """Susurra un mensaje por cada Caliban que conoce el usuario, con tirada independiente por cada uno."""
    user_id = not_none(interaction.user).id
    caliban_group_id = get_caliban_met(user_id)
    for caliban_name, chance in CALIBAN_GROUPS.get(caliban_group_id, []):
        if random.randint(1, 100) <= chance:
            message = get_random_message(caliban_name, type)
            await send_caliban_message(interaction, caliban_name, message)


async def caliban_force_speaks(interaction: Interaction, message: str, caliban_name: str = "caliban") -> None:
    """Fuerza un mensaje específico de un Caliban concreto, si el usuario lo conoce."""
    user_id = not_none(interaction.user).id
    caliban_group_id = get_caliban_met(user_id)
    group_names = [name for name, _ in CALIBAN_GROUPS.get(caliban_group_id, [])]
    if caliban_name in group_names:
        await send_caliban_message(interaction, caliban_name, message)


def get_random_message(caliban_name: str, type: MessageType = "default") -> str:
    """Devuelve un mensaje aleatorio del Caliban especificado según el tipo. Usa 'default' si el tipo no existe."""
    caliban = CALIBANS[caliban_name]
    pool = caliban["messages"].get(type) or caliban["messages"]["default"]
    return random.choice(pool)


async def send_caliban_message(
    interaction: Interaction,
    caliban_name: str,
    message: str | None,
) -> None:
    """Envía un mensaje de un Caliban concreto al usuario."""
    if not message:
        return

    caliban = CALIBANS[caliban_name]
    embed = Embed(description=f"`{message}`", color=Color.greyple())
    embed.set_author(name=caliban["name"])
    embed.set_thumbnail(url=caliban["image"])
    await interaction.followup.send(embed=embed, ephemeral=True, delete_after=5)
