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
    "Elohim": {
        "type": "Default",
        "message": {
            "default": [
                "Eres uno de los muchos que observo esta noche. No confundas eso con insignificancia.",
                "Actua. Lo registraré fielmente y, en su mayor parte, sin juzgar.",
                "Estás siendo observado. Que eso te preocupe o no dice más de ti que de mí.",
                "Tengo muchos ojos, y esta noche, varios de ellos están puestos en ti.",
                "¿Sientes eso? Soy yo, prestándote atención específicamente, por un momento.",
                "Continúa. Simplemente observo, como fui creado para hacerlo.",
                "Estoy observando. Siempre estoy observando.",
                "Esta noche, la radio transmite cien mentiras. Yo no transmito ninguna. Continúa.",
                "Las fronteras se cierran y se abren, los ejércitos redibujan el mapa... y sigo vigilando esta habitación.",
                "Esta noche, en algún lugar, un tren cruza una frontera que no debería. No estoy observando eso. Te estoy observando a ti.",
                "La Confederación se autodenomina neutral. Yo me considero observador. Continúa.",
                "Sirves a un país fingiendo que no tiene bando. Yo no tengo esa pretensión. Veo todos los bandos.",
                "Las montañas guardan bien los secretos de este país. Yo guardo mejores. Sigue.",
                "Esta noche, todos los gobiernos de Europa le mienten a alguien. Mentir me resulta tedioso. Continúa con la verdad."
            ],
            "success": [
                "Has triunfado. Él también te está observando, me imagino, y sospecho que está complacido."
                "Un éxito rotundo. He visto cosas peores en manos mucho más experimentadas.",
                "La fortuna está de tu lado esta vez. No te acostumbres a ella.",
                "Eso funcionó. Confieso que sentí un pizca de aprobación.",
                "Bien hecho. No lo digo a la ligera, ni a menudo.",
                "Todo sale como uno quiere. Las pequeñas victorias se acumulan y, con el tiempo, dan lugar a algo importante.",
                "El resultado te favorece. Tomaré nota.",
                "Lo has conseguido. La noche es un poco menos oscura gracias a ello.",
                "Éxito. Un pequeño detalle que sale bien en un mundo que, por ahora, está diseñado para ir mal.",
                "Bien hecho. Ni siquiera la cuidadosa neutralidad de Berna puede atribuirse este mérito.",
                "Acertado. En algún lugar se presentará un informe, y no mencionará quién eres realmente.",
                "Lo has conseguido. Los secretos de la Confederación, por esta noche, seguirán siendo secretos.",
                "Una victoria limpia, en una década que ha olvidado cómo son esas victorias.",
                "Éxito. Independientemente de lo que Berlín o Londres crean que está sucediendo aquí esta noche, no es esto.",
                "Bien jugado. Incluso en terreno neutral se necesita a alguien competente para mantenerse firme."
            ],
            "failure": [
                "Las cosas no salen como esperabas. Estas cosas pasan, incluso bajo mi mirada.",
                "El intento no da resultado. Habrá otros.",
                "No se consigue nada. He visto resultados mucho peores que un simple fracaso.",
                "Se te escapa de las manos. Inténtalo de nuevo, si es que puedes.",
                "Aquí no encuentras el éxito. Ten paciencia. La paciencia es más antigua que todos vosotros.",
                "El resultado decepciona. He presenciado noches peores que esta.",
                "No funciona. La verdad es que, al menos, no me sorprende.",
                "Las cosas no salen como esperas. La guerra no se detiene a observar, y yo tampoco, en particular.",
                "Un fracaso. Algo insignificante, en un año repleto de fracasos mucho mayores.",
                "No se logra. Inténtalo de nuevo; lamentablemente, la guerra seguirá aquí cuando lo consigas.",
                "Esta noche no hay éxito. Paciencia. La neutralidad en sí misma es, en gran medida, paciencia disfrazada de política.",
                "Se nos escapa de las manos. La Confederación ha sobrevivido descuidos peores que el de esta noche.",
                "Un esfuerzo fallido. He visto frentes enteros colapsar por motivos menores.",
                "El resultado es decepcionante. He registrado decepciones peores en Berlín este mes."
            ],
            "botch": [
                "Eso fue catastrófico. Ni yo me lo esperaba.",
                "Un desastre, claro e innegable. Estaré muy atento.",
                "El momento se vuelve completamente en tu contra. Yo tendría cuidado, si fuera capaz de preocuparme.",
                "Ruina, inequívoca e inmediata. Espero que tengas un plan para lo que viene.",
                "El mundo entero parece estar en tu contra esta noche. Fuertemente.",
                "Catástrofe. Registraré esto con detalle.",
                "Algo se ha deshecho con ese fallo. Sugiero abordarlo cuanto antes.",
                "Catastrófico. Espero que nadie importante para ti estuviera mirando, porque yo sí que lo estaba.",
                "Ruina, simple y llanamente. Confío en que tienes una historia preparada para quien te la pida.",
                "Eso no solo fracasó, sino que se rompió estrepitosamente en un país que valora la tranquilidad por encima de casi todo.",
                "Un auténtico desastre. Tan raro que alguien en una oficina gris acabará oyendo de aquello.",
                "Un desastre, y uno muy inconveniente; Berna no perdona los inconvenientes fácilmente.",
                "Catástrofe. Voy a documentar esto con todo detalle, y sospecho que alguien en la OFP también lo hará.",
                "Ese fracaso deja algo sin resolver. Me encargaria de aquello antes de que Berlín, Londres o Berna se den cuenta."
            ],
        }
    },
    "Vampire": {
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
                "Hábilmente ejecutado. Al verte trabajar en las sombras de Berna, casi olvido lo que eres.",
                "Victoria. Gástala con sabiduría - la suerte no es un recurso que tu especie reponga fácilmente.",
                "La rueda gira a tu favor. Yo hago girar muchas ruedas. Esta, no la toqué.",
                "La suerte te favorece esta noche, hijo de Caín, mientras Berna duerme ajena a lo que camina por sus calles.",
                "Éxito. Incluso en un país neutral, gente como tú encuentra la manera de ganar discretamente.",
                "La fortuna sonríe aquí, en ese rincón de Europa que finge no estar en guerra. Muy conveniente para ti.",
                "Victoria. Úsala con prudencia: la paciencia de la Confederación con sus silenciosos monstruos no es infinita.",
                "La rueda gira a tu favor. Roma ardió una vez. Berna simplemente presenta papeleo. Lo hiciste bien dentro de ese marco.",
                "Tienes éxito, y en algún lugar un funcionario suizo firma un formulario que jamás mencionará lo que realmente sucedió."
            ],
            "failure": [
                "Esta noche no tendrás éxito. Quizás la Bestia hace demasiado ruido para oír mi consejo.",
                "Fracaso. Les ocurre incluso a quienes ya no envejecen.",
                "Siglos de no-vida y aun así la suerte te humillan.",
                "No consigues nada. Tu paciencia, a diferencia de tu cuerpo, sigue siendo mortal en sus límites.",
                "Las cosas no salen como esperabas. La inmortalidad enseña paciencia, o debería haberlo hecho ya.",
                "Una noche infructuosa. Esperemos que tu Bestia no la empeore.",
                "Fracaso, simple y corriente. Incluso los Condenados tienen noches ordinarias.",
                "El intento se derrumba, silenciosamente, como todo aquí debe hacerlo.",
                "De esto no se saca nada en claro. Tu paciencia debería ser mayor que la de una nación, y esta noche no lo fue.",
                "Una noche de fracaso, en un país construido enteramente sobre la base de que las noches de fracaso pasan desapercibidas.",
                "Las cosas no salen como uno quiere. Ni siquiera la neutralidad puede comprar la buena suerte.",
                "Fracaso, simple y llanamente, algo raro en un año que se empeña en ser extraordinario en todos los demás aspectos."
            ],
            "botch": [
                "La Bestia se rió de eso. A mí no me hizo ninguna gracia.",
                "Eso no fue simplemente un fracaso, fue el universo tomándote como una crueldad.",
                "Ruina, y es enteramente tuya. La Bestia dirá lo contrario. La Bestia miente.",
                "Un desastre, hijo de la noche. Algo se ha roto ahora que no lo estaba hace un momento.",
                "Desastre. He visto a ancianos arruinados por noches que comenzaron exactamente como esta.",
                "La noche misma parece rechazarte. No la culpo del todo.",
                "La suerte se vuelven completamente en tu contra. Me pregunto si Caín sintió esto alguna vez.",
                "La Bestia se rió de eso. En algún lugar, una patrulla se convirtió en un problema muy inmediato.",
                "Catástrofe. Incluso en terreno neutral hay noches terribles, y acabas de encontrarte con una de las peores de Berna.",
                "Eso no fue un simple fracaso. Fue el tipo de error que termina archivado y que alguien quema más tarde.",
                "Aquí, donde la discreción es la religión nacional, la suerte te maldice a gritos.",
                "Un desastre, hijo de la noche, en el único país de Europa que no puede permitirse semejantes errores.",
                "Esto tendrá consecuencias más allá de esta noche, y Berna lleva un registro muy preciso de las consecuencias.",
                "Te has vuelto enemigo del momento, y posiblemente de algun agente federal. Un trabajo excepcional."
            ],
        }
    },
    "Mage": {
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
                "Maestría demostrada. He visto morir a otros Iluminados por intentar menos.",
                "La fórmula se mantiene. La verdad es que estoy un poco impresionado."
                "El Tapiz se doblegó a tu voluntad, aquí, al borde de un continente que se desgarra a sí mismo. Eso no es poca cosa.",
                "Bien hecho. Incluso entre cortinas opacas y comidas racionados, la realidad cedio a ti en este momento.",
                "El patrón obedece, silenciosamente, la forma en que todo en este país debería hacerlo.",
                "Una muestra de maestría, en una nación que ha hecho un arte el aparentar no hacer absolutamente nada.",
                "La fórmula se mantiene, más estable que la mayoría de las fronteras europeas en la actualidad.",
                "Esta noche, vuestra voluntad y la del mundo coinciden. Ojalá pudiera decir lo mismo de los Aliados y del Reich.",
                "Bien hecho. Bern nunca sabrá lo que casi salió mal aquí, y ese es precisamente el punto."
            ],
            "failure": [
                "El patrón se resiste. La realidad, a veces, tiene sus propias opiniones.",
                "Tu voluntad se encuentra con la del mundo y, esta vez, pierde.",
                "Intentas, y el Tapiz no responde. Sucede, incluso a los Iluminados.",
                "El mundo rechaza tu petición hoy. Al menos, fue con cortesía.",
                "No funciona. Inténtalo de nuevo... o no. No sere quien pague por un segundo intento.",
                "Tu Avatar guarda silencio sobre esto. Quizás no estuvo de acuerdo con el intento.",
                "Nada cambia. Para un Iluminado, ese puede ser el resultado más extraño de todos.",
                "El patron se resiste, aquí donde incluso las montañas parecen contener la respiración.",
                "La fórmula queda corta. Incluso la magia sufre bajo un continente en llamas.",
                "Intentas deshacerlo, pero el Tapiz no responde; no todos los nudos se deshacen a la orden.",
                "Sin éxito. Agradece que no te haya costado nada más que el intento, especialmente en esta epoca.",
                "El mundo rechaza tu petición. Con toda cortesía; al fin y al cabo, esto sigue siendo Suiza.",
                "Tu Avatar está en silencio esta noche. Quizás incluso aquello presiente lo estrepitoso que sería un error aquí.",
                "Nada cambia. En un país cuya política se basa precisamente en que nada cambie, quizás sea apropiado."
            ],
            "botch": [
                "El Tapiz no solo se resiste, sino que contraataca. Prepárate.",
                "La realidad se lo ha tomado como algo personal. Esto no se quedará callado.",
                "Un desastre, Iluminado. En algún lugar, el mundo está decidiendo cómo castigar las libertades que te has tomado.",
                "Tu voluntad se rebeló contra la del mundo, y el mundo no perdona fácilmente ese intento.",
                "La fórmula no solo falló, sino que se invirtió. Yo no me quedaría ahí parado, si fuera tú.",
                "La Paradoja no olvida. Esta noche, le diste mucho que recordar.",
                "El universo se resiste con fuerza. Así sabe la arrogancia.",
                "La Paradoja se agita, hambrienta, en un país que ya tiene suficientes problemas sin explicacion esta década.",
                "La realidad se lo ha tomado como algo personal, y la paciencia de Bern no tardará en agotarse.",
                "Tu voluntad se rebeló contra la del mundo, y a diferencia de la diplomacia suiza, el mundo no se lo toma con delicadeza.",
                "Algo se ha soltado, algo que debería haber permanecido atado. Encuéntralo antes del toque de queda, si es que puedes.",
                "La Paradoja no olvida y, según he observado, tampoco lo hace el registro federal suizo.",
                "El universo se resiste con fuerza en un país cuya estrategia se basa precisamente en aparentar no resistirse.",
                "Catastrófico. Tu Avatar está tan alarmado como las autoridades locales cuando se enteren."
            ],
        }
    },
    "Hunter": {
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
                "Éxito, mortal: sin disciplina, sin esfera, solo manos firmes en un país que finge que no hay guerra.",
                "Triunfas donde criaturas más antiguas que la propia Confederación a menudo fracasan. Reflexiona sobre eso.",
                "Un triunfo mortal. Confieso que me resultan más conmovedores que los demás.",
                "Bien ejecutado, llama pequeña y certera, en una decada decidida a apagar todas las que encuentra.",
                "Éxito. Anótalo en algún sitio; las victorias mortales se pierden fácilmente en el tiempo.",
                "Triunfas esta noche. Mañana tendrás que volver a hacerlo. Así es la condición mortal.",
                "La convicción se transformó en acción, y acertó de lleno."
                "Bien hecho. Suiza se autodenomina neutral. Esta noche, tu no has estado ociosos.",
                "Tu Convicción se afila con acciones, en el último país tranquilo que queda en Europa.",
                "Tu fe no fallo, ni siquiera bajo cielos completamente oscuros y con cien kilómetros de frontera que vigilar.",
                "Un triunfo mortal, sin registro en ningún sitio, sin atribuirse a nadie, exactamente como a Berna le gusta.",
                "Usted mismo lo hizo, en una guerra que Berna insiste no estar involucrada.",
                "Éxito. Anótalo en algún lugar donde ningún funcionario lo lea jamás.",
                "Esta noche triunfarás. Mañana, las fronteras cambiaran, y tendrás que volver a hacerlo."
            ],
            "failure": [
                "No funciona, mortal. Esos errores están permitidos. De hecho, a menudo.",
                "Tu convicción o tu puntería ha falló. Cualquiera de las dos se remediará mañana.",
                "Un intento fallido. Él no te ama menos por ello.",
                "Fallaste. Descansa. Incluso los elegidos necesitan descansar.",
                "No tuviste éxito esta noche. He visto ejércitos fracasar por razones menores que la tuya.",
                "No aciertas. Inténtalo de nuevo cuando tengas las manos más firmes.",
                "Te quedas corto. La mortalidad se compone principalmente de quedarse corto y de intentarlo a pesar de todo.",
                "No funciona, mortal. Esos errores están permitidos, incluso en una guerra en la que técnicamente no participas.",
                "Fracasas. No hay maldición a la que culpar; solo cuerpo mortal, frío y una frontera muy larga que vigilar.",
                "Tu puntería fallo. Descansa; Berna ocultará las pruebas de una mala noche.",
                "Fallaste. Incluso el país neutral que te rodea está teniendo un noche difícil como esta.",
                "Fracaso, y sin una excusa sobrenatural tras la que esconderse. Eso requiere su propio tipo de valentía.",
                "Te quedas corto. Como la diplomacia de todos este año. Al menos, estás en buena compañía."
            ],
            "botch": [
                "Un fallo garrafal, mortal. Ni Bestia, ni Paradoja a quien culpar; solo el azar, y se volvió cruelmente contra ti.",
                "La desgracia te encuentra. Confieso que no esperaba que Él permitiera esto.",
                "Tu convicción se resquebrajó justo en el peor momento. Estas cosas también les pasan a los fieles.",
                "Un giro terrible. La suerte de los mortales es algo muy caprichoso.",
                "Catástrofico, simple y mortal. Dejará heridas. Puede que sea peor que un simple moreton.",
                "El momento se ha vuelto violentamente en tu contra. Reacciona; ahora tendrás que ser rápido.",
                "La ruina te encuentra desprotegido, sin maldición ni don. Ese es el pacto mortal, en su totalidad.",
                "Un fallo garrafal, mortal. No hay maldición ni despertar que lo impida, solo el azar que se vuelve cruel en un país muy frío.",
                "Algo ha salido muy mal, y no hay ninguna explicación sobrenatural para aquello.",
                "Esto dolerá, y no hay disciplina ni esfera que pueda adormecerlo. Lo siento, de verdad, esta vez.",
                "Catástrofe, simple y mortal, en una nación con muy poca tolerancia para esos resultados este año.",
                "La situación se ha vuelto violentamente en tu contra. Muévete rápido; Berna ya no te puede proteger.",
                "Un desastre. Ni siquiera los elegidos se libran de esto, especialmente en una guerra que pretende no afectarles."
            ],
        }
    },
}


def elohim_quote(interaction: Interaction, type: MessageType = "default") -> str | None:
    user_id = not_none(interaction.user).id
    pj = PJsController.cached().get_pj_row(user_id)
    elohim = random.choice([pj.Char_type, "Elohim"])
    return get_random_message(elohim, type)


def get_random_message(elohim: str, type: MessageType = "default") -> str:
    elohim_type = ELOHIM[elohim]
    pool = elohim_type["message"].get(
        type) or elohim_type["message"]["default"]
    return random.choice(pool)


def quotify(text: str, interaction: Interaction, type: MessageType = "default", chance: int = 20) -> str:
    r = random.randint(1, 100) <= chance
    if r:
        quote = elohim_quote(interaction, type)
        quote = f"\n\n*{quote}*"
        return f"{text}{quote}"
    return text

# async def send_elohim_message(
#        interaction: Interaction,
#        message: str | None,
# ) -> None:
#    if not message:
#        return
#    await interaction.followup.send(f"`{message}`")

# async def elohim_speaks(interaction: Interaction, type: MessageType = "default") -> None:
#    user_id = not_none(interaction.user).id
#    pj = PJsController.cached().get_pj_row(user_id)
#    if random.randint(1,100) <= 15:
#        elohim = random.choice([pj.Char_type, "Elohim"])
#        message = get_random_message(elohim,type)
#        await send_elohim_message(interaction, message)
