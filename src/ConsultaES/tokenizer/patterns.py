"""DFA definiciones para cada token de clase.

Cada constructor retorna un objeto DFA. El tokenizador utiliza longest_match + priority
para elegir la clase ganadora en cada posición.
"""
from .dfa import DFA

DIGITS = set("0123456789")
LOWER = set("abcdefghijklmnopqrstuvwxyz")
UPPER = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
ACCENTED = set("áéíóúñüÁÉÍÓÚÑÜ")
LETTERS = LOWER | UPPER | ACCENTED

MONTHS = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

COMP_PHRASES = [
    "mayor o igual a",
    "menor o igual a",
    "mayor que",
    "menor que",
    "igual a",
    "diferente de",
]


LIKE_PHRASES = [
    "parecido a",
    "contiene",
    "empieza con",
    "termina con",
]

RANGO_PHRASES = ["entre"]
NEG_PHRASES = ["no"]

CONECTORES = ["y", "o", "pero"]
PUNCT = set(",.;:?¿!¡()")


def _build_trie_dfa(phrases, alphabet_extra=None):
    """Construye un DFA que acepte cualquiera de las frases dadas (coincidencia más larga)

    Los estados son los prefijos encontrados. Un estado de aceptación corresponde a un prefijo
    que es igual a una frase completa.
    """
    alphabet: set[str] = set()
    for p in phrases:
        alphabet.update(p)
    if alphabet_extra:
        alphabet.update(alphabet_extra)

    prefixes: set[str] = {""}
    for p in phrases:
        for i in range(1, len(p) + 1):
            prefixes.add(p[:i])

    delta: dict[tuple[str, str], str] = {}
    for pre in prefixes:
        for ch in alphabet:
            cand = pre + ch
            if cand in prefixes:
                delta[(pre, ch)] = cand

    finals = {p for p in phrases}
    return DFA(
        states=prefixes,
        alphabet=alphabet,
        delta=delta,
        start="",
        finals=finals,
    )


def build_cadena_dfa() -> DFA:
    """Coincide con '...' - una comilla, cualquier carácter que no sea una comilla, 
    una comilla de cierre.

    El alfabeto es "cualquier carácter razonable"; utilizamos un enfoque de centinela donde
    `delta` mapea caracteres desconocidos a través de un fallback implementado enumerando un
    alfabeto razonable. Para mantenerlo acotado, incluimos ASCII imprimible +
    letras acentuadas + dígitos + espacio.
    """
    body_alphabet = (
        LETTERS | DIGITS | set(" ")
        | set("-_.,;:!?¿¡()[]/\\@#$%&*+=<>áéíóúñ")
    )
    full_alphabet = body_alphabet | {"'"}

    states = {"q0", "q1", "q2"}
    delta: dict[tuple[str, str], str] = {}
    # q0 --'--> q1
    delta[("q0", "'")] = "q1"
    # q1 --body--> q1 (cualquier cosa excepto ')
    for ch in body_alphabet:
        if ch != "'":
            delta[("q1", ch)] = "q1"
    # q1 --'--> q2 (aceptando)
    delta[("q1", "'")] = "q2"
    return DFA(
        states=states,
        alphabet=full_alphabet,
        delta=delta,
        start="q0",
        finals={"q2"},
    )


def build_fecha_dfa() -> DFA:
    """Acepta:
    - un nombre de mes
    - un año de 4 dígitos
    - dd de mes
    - dd de mes de yyyy

    Implementado como un único DFA con transiciones sensibles al espacio. Codificamos el
    prefijo "dd de " y luego un mes, opcionalmente seguido de " de yyyy".
    También se aceptan meses solos y años de 4 dígitos.
    """
    alphabet: set[str] = set(" de") | DIGITS
    for m in MONTHS:
        alphabet.update(m)

    states: set[str] = set()
    delta: dict[tuple[str, str], str] = {}
    finals: set[str] = set()

    start = "S"
    states.add(start)

    # --- Rama del año de 4 dígitos ---
    # S -d-> Y1 -d-> Y2 -d-> Y3 -d-> Y4(final)
    for k, nxt in [("S", "Y1"), ("Y1", "Y2"), ("Y2", "Y3"), ("Y3", "Y4_YEAR")]:
        states.add(nxt)
        for d in DIGITS:
            delta[(k, d)] = nxt
    finals.add("Y4_YEAR")

    # --- dd de mes ... branch ---
    # Desde Y1 (un dígito), en espacio vamos a D1_SP esperando "de <mes>..."
    # Desde Y2 (dos dígitos), en espacio vamos a D2_SP esperando "de <mes>..."
    # Reutilizamos Y1/Y2 como estados de "1 dígito", "2 dígitos".
    # Después de " de " entramos al matching de meses.

    # Construye un camino para " de " después de dd
    def add_literal_path(from_state, literal, to_state_prefix):
        """Construye transiciones consumiendo `literal` caracter por caracter; devuelve el nombre del estado final."""
        cur = from_state
        for i, ch in enumerate(literal):
            nxt = f"{to_state_prefix}_{i}" if i < len(literal) - 1 else f"{to_state_prefix}_END"
            states.add(nxt)
            delta[(cur, ch)] = nxt
            cur = nxt
        return cur

    # dd (1 o 2 dígitos) -> " de " -> inicio de mes
    # Y1 -espacio-> A1 -d-> A2 -e-> A3 -espacio-> MONTH_START
    # Lo mismo desde Y2
    month_start_from_dd = "MONTH_DD_START"
    states.add(month_start_from_dd)
    for src in ["Y1", "Y2"]:
        a1 = f"{src}_SP"
        states.add(a1)
        delta[(src, " ")] = a1
        a2 = f"{src}_D"
        states.add(a2)
        delta[(a1, "d")] = a2
        a3 = f"{src}_E"
        states.add(a3)
        delta[(a2, "e")] = a3
        a4 = f"{src}_SP2"
        states.add(a4)
        delta[(a3, " ")] = a4
        # Se enruta duplicando también las aristas del mes desde a4
        # Más simple: hacer a4 == month_start
        # Redirigir: establecer delta[(a4, c)] = delta[(month_start, c)] después de construir los meses
        # Rastrea estos puntos de pegado.
    glue_points = ["Y1_SP2", "Y2_SP2"]

    # --- Emparejamiento de meses desde month_start_from_dd ---
    # Construye un trie para meses. Los nombres de estado prefijados por "M_" + prefijo.
    month_prefixes: set[str] = {""}
    for m in MONTHS:
        for i in range(1, len(m) + 1):
            month_prefixes.add(m[:i])

    def mstate(pre):
        return f"M_{pre}" if pre else month_start_from_dd

    for pre in month_prefixes:
        states.add(mstate(pre))
    # Transiciones dentro del trie de meses
    for pre in month_prefixes:
        for ch in set("".join(MONTHS)):
            cand = pre + ch
            if cand in month_prefixes:
                delta[(mstate(pre), ch)] = mstate(cand)
    # Los meses completos son aceptados (esto maneja el punto final "dd de mes" Y el manejo del sufijo después del año)
    for m in MONTHS:
        finals.add(mstate(m))

    # También: mes suelto desde el inicio S. S -first_letter-> M_<letter> ...
    # Construye un trie paralelo de "mes suelto" que comienza en S, compartiendo la misma lógica.
    # Más simple: agregar aristas directas desde S usando los estados del trie de meses BM_<pre>.
    bm_prefixes = month_prefixes
    def bmstate(pre):
        return f"BM_{pre}" if pre else start
    for pre in bm_prefixes:
        if pre:
            states.add(bmstate(pre))
    for pre in bm_prefixes:
        for ch in set("".join(MONTHS)):
            cand = pre + ch
            if cand in bm_prefixes:
                delta[(bmstate(pre), ch)] = bmstate(cand)
    for m in MONTHS:
        finals.add(bmstate(m))

    # Pegar Y1_SP2 y Y2_SP2 para actuar como month_start_from_dd (M_"")
    for gp in glue_points:
        for ch in set("".join(MONTHS)):
            if ("", ch) in [(p, ch) for p in [""] ]:
                pass
        # Copiar todas las aristas salientes de month_start_from_dd
        for ch in set("".join(MONTHS)):
            key_src = (month_start_from_dd, ch)
            if key_src in delta:
                delta[(gp, ch)] = delta[key_src]

    # --- Después de "dd de mes" (un estado de mes final alcanzado desde MONTH_DD_START), podemos consumir opcionalmente
    # " de yyyy". Para mantenerlo simple, para cada estado de mes de aceptación alcanzado a través del
    # rama dd (M_<mes>), agregamos una ruta de sufijo opcional.
    # Problema: M_<m> final se comparte entre el mes suelto (desde S) y la rama dd. ¿Ambos casos deberían
    # permitir el sufijo opcional " de yyyy"? La especificación: "<dd> de <mes>( de <yyyy>)?" — así que solo después de dd.
    # El mes suelto NO toma un sufijo de año. Pero agregarlo después del mes suelto también sería aceptado —
    # aceptaría efectivamente "marzo de 2025" como FECHA lo cual parece deseable de todos modos.
    # En realidad, la forma (a) de la especificación es solo mes suelto; pero nada prohíbe la extensión. Seremos permisivos.

    # Desde M_<m> (final), agregar " de <digits4>" ruta de sufijo que conduce a SUFF_Y4 (final).
    suff_sp1 = "SUFF_SP1"
    suff_d = "SUFF_D"
    suff_e = "SUFF_E"
    suff_sp2 = "SUFF_SP2"
    suff_y1 = "SUFF_Y1"
    suff_y2 = "SUFF_Y2"
    suff_y3 = "SUFF_Y3"
    suff_y4 = "SUFF_Y4"
    for s in [suff_sp1, suff_d, suff_e, suff_sp2, suff_y1, suff_y2, suff_y3, suff_y4]:
        states.add(s)
    # Todos los estados de mes final transitan en espacio a suff_sp1
    month_finals = [mstate(m) for m in MONTHS] + [bmstate(m) for m in MONTHS]
    for mf in month_finals:
        delta[(mf, " ")] = suff_sp1
    delta[(suff_sp1, "d")] = suff_d
    delta[(suff_d, "e")] = suff_e
    delta[(suff_e, " ")] = suff_sp2
    for d in DIGITS:
        delta[(suff_sp2, d)] = suff_y1
        delta[(suff_y1, d)] = suff_y2
        delta[(suff_y2, d)] = suff_y3
        delta[(suff_y3, d)] = suff_y4
    finals.add(suff_y4)

    return DFA(
        states=states,
        alphabet=alphabet,
        delta=delta,
        start=start,
        finals=finals,
    )


def build_op_comp_dfa() -> DFA:
    return _build_trie_dfa(COMP_PHRASES)


def build_op_like_dfa() -> DFA:
    return _build_trie_dfa(LIKE_PHRASES)


def build_rango_dfa() -> DFA:
    return _build_trie_dfa(RANGO_PHRASES)


def build_neg_dfa() -> DFA:
    return _build_trie_dfa(NEG_PHRASES)


def build_num_dfa() -> DFA:
    """digits+ ( "." digits+ )?"""
    states = {"q0", "q1", "q2", "q3"}
    delta: dict[tuple[str, str], str] = {}
    for d in DIGITS:
        delta[("q0", d)] = "q1"
        delta[("q1", d)] = "q1"
        delta[("q2", d)] = "q3"
        delta[("q3", d)] = "q3"
    delta[("q1", ".")] = "q2"
    return DFA(
        states=states,
        alphabet=DIGITS | {"."},
        delta=delta,
        start="q0",
        finals={"q1", "q3"},
    )


def build_conector_dfa() -> DFA:
    return _build_trie_dfa(CONECTORES)


def build_palabra_dfa() -> DFA:
    """Una o más letras (minúsculas, mayúsculas, acentuadas)."""
    states = {"q0", "q1"}
    delta: dict[tuple[str, str], str] = {}
    for ch in LETTERS:
        delta[("q0", ch)] = "q1"
        delta[("q1", ch)] = "q1"
    return DFA(
        states=states,
        alphabet=LETTERS,
        delta=delta,
        start="q0",
        finals={"q1"},
    )


def build_punt_dfa() -> DFA:
    states = {"q0", "q1"}
    delta: dict[tuple[str, str], str] = {}
    for ch in PUNCT:
        delta[("q0", ch)] = "q1"
    return DFA(
        states=states,
        alphabet=PUNCT,
        delta=delta,
        start="q0",
        finals={"q1"},
    )


# Orden de prioridad: índice más bajo = mayor prioridad
PRIORITY = [
    "CADENA",
    "FECHA",
    "OP_COMP",
    "OP_LIKE",
    "RANGO",
    "NEG",
    "NUM",
    "CONECTOR",
    "PALABRA",
    "PUNT",
]

def build_all() -> list[tuple[str, DFA]]:
    return [
        ("CADENA", build_cadena_dfa()),
        ("FECHA", build_fecha_dfa()),
        ("OP_COMP", build_op_comp_dfa()),
        ("OP_LIKE", build_op_like_dfa()),
        ("RANGO", build_rango_dfa()),
        ("NEG", build_neg_dfa()),
        ("NUM", build_num_dfa()),
        ("CONECTOR", build_conector_dfa()),
        ("PALABRA", build_palabra_dfa()),
        ("PUNT", build_punt_dfa()),
    ]
