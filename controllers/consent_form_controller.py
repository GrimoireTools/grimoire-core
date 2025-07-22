"""Consent Form Controller Module."""

from controllers.lib.base_controller import SheetsControllerBase
from controllers.lib.row import Row

CONSENT_FORM_SHEET_ID = 1780466578
CONSENT_FORM_DOC_NAME = "CRO Consent Form"

COLUMN_DESCRIPTIONS = {
    "Timestamp": "Fecha y hora de envío del formulario",
    "Discord_id": "Identificador único de Discord del jugador",
    "Player_name": "Nombre del jugador (opcional)",
    "Aranas_insectos": "Temas relacionados a arañas e insectos",
    "Sangre_gore": "Sangre y contenido gore",
    "Body_horror": "Horror corporal y escenas grotescas",
    "Demons": "Demonios y criaturas sobrenaturales",
    "Psicologic_horror": "Terror psicológico",
    "Sec1_other": "Otros temas de terror y horror no mencionados",
    "Sex_gender": "Temáticas de sexo y género",
    "Romance_general": "Escenas románticas en general",
    "Romance_pj_npc": "Romance entre personaje jugador y NPC",
    "Romance_pj_pj": "Romance entre personajes jugadores",
    "Flirting": "Coqueteo e insinuaciones",
    "Abusive_relations": "Relaciones abusivas",
    "Explicit_scenes": "Escenas explícitas",
    "Sec2_other": "Otros temas de relaciones no mencionados",
    "Discrimination": "Temas de discriminación",
    "Classism": "Clasismo y desigualdad social",
    "Racism": "Racismo y xenofobia",
    "Lgbtphobia": "Homofobia o transfobia",
    "Religion": "Temas de religión y fanatismo",
    "War": "Guerra y conflictos",
    "Slavery": "Esclavitud o trata de personas",
    "Gender_violence": "Violencia de género",
    "Explicit_violence": "Violencia explícita o simbólica",
    "Sec3_other": "Otros temas socioculturales no mencionados",
    "Self_harm": "Autolesiones",
    "Cancer": "Temas de cáncer",
    "Chronic_illness": "Enfermedades crónicas",
    "Natural_disasters": "Desastres naturales",
    "Pregnancy": "Embarazos, pérdidas y aborto",
    "Torture": "Tortura física o psicológica",
    "Mental_health": "Temas de salud mental",
    "Phobias": "Fobias y traumas",
    "Death_scenes": "Escenas explícitas de daños o muerte",
    "Sec4_other": "Otros temas de salud física/mental no mencionados",
    "Feedback": "Comentarios adicionales sobre los temas del formulario",
}

ConsentOptions = {
    "Si": 0,
    "Bueno, pero fuera de cámara": 1,
    "No": 2,
}

non_consent_options = [
    "Timestamp",
    "Discord_id",
    "Player_name",
]


class ConsentFormRow(Row):
    """Row for a consent form response."""

    # - Sección 0
    Timestamp: str  # Marca temporal
    Discord_id: str  # ID de discord
    Player_name: str  # Nombre del jugador o jugadora (También puede dejarse en blanco)
    # - Sección 1: Terror y Horror
    Aranas_insectos: str  # Arañas e insectos
    Sangre_gore: str  # Sangre /Contenido Gore
    Body_horror: str  # Body Horror/Escenas grotescas
    Demons: str  # Demonios/Criaturas sobrenaturales
    Psicologic_horror: str  # Terror Psicológico
    Sec1_other: str  # ¿Algún otro tema que incluirías aquí?
    # - Sección 2: Relaciones
    Sex_gender: str  # Exploración de temáticas sexo-género
    Romance_general: str  # Escenas románticas en general
    Romance_pj_npc: str  # Romance entre PJ - NPC
    Romance_pj_pj: str  # Romance entre PJ - PJ
    Flirting: str  # Coqueteo e insinuaciones
    Abusive_relations: str  # Relaciones con situaciones de abuso
    Explicit_scenes: str  # Escenas explícitas
    Sec2_other: str  # ¿Algún otro tema que incluirías aquí?
    # - Sección 3: Problemáticas Socioculturales
    Discrimination: str  # Discriminación en general
    Classism: str  # Clasismo y Desigualdad Social
    Racism: str  # Racismo y Xenofobia
    Lgbtphobia: str  # Homofobia o Transfobia
    Religion: str  # Religión y Fanatismo
    War: str  # Guerra y Conflictos
    Slavery: str  # Esclavitud o Trata de personas
    Gender_violence: str  # Violencia de género
    Explicit_violence: str  # Violencia explícita o simbólica
    Sec3_other: str  # ¿Algún otro tema que incluirías aquí?
    # - Sección 4: Probemas de salud física/mental
    Self_harm: str  # Autolesiones
    Cancer: str  # Cáncer
    Chronic_illness: str  # Enfermedades crónicas
    Natural_disasters: str  # Desastres naturales (inundaciones, incendios, terremotos, etc.)
    Pregnancy: str  # Embarazos, pérdidas, aborto
    Torture: str  # Tortura física o psicológica
    Mental_health: str  # Salud mental
    Phobias: str  # Fobias y Traumas
    Death_scenes: str  # Escenas explícitas de daños o muerte
    Sec4_other: str  # ¿Algún otro tema que incluirías aquí?
    # - Sección 5: Feedback
    # ¿Te gustaría comentar sobre algun de estos temas o sobre alguno que no se haya abordado aquí?
    # Si es así, ¿cuál/es?
    Feedback: str

    def notable_options(self) -> list[str]:
        """Devuelve una lista de opciones que son notables (no "Sí")."""
        notable_options = []
        for col, description in COLUMN_DESCRIPTIONS.items():
            if col in non_consent_options:
                continue
            val = self.__getattribute__(col)
            if not val or ConsentOptions.get(val, 1) == ConsentOptions["Si"]:
                continue
            notable_options.append(f"{description}: {val}")
        return notable_options


class ConsentFormController(SheetsControllerBase[ConsentFormRow]):
    """Controller for managing consent form responses."""

    def __init__(self) -> None:
        super().__init__(CONSENT_FORM_SHEET_ID, ConsentFormRow, CONSENT_FORM_DOC_NAME)

    def get_latest_response(self, discord_id: int) -> ConsentFormRow | None:
        """Devuelve las última respuesta de un usuario, o None si no ha respondido."""
        try:
            rows = self.find_rows_with_values(
                {
                    "Discord_id": str(discord_id),
                }
            )
            if len(rows) == 0:
                return None
            # Ordena las filas por la marca de tiempo
            return rows[-1]
        except ValueError:
            return None
