"""Capa 3 del desambiguador: paráfrasis en español + diálogo de elección.

Genera una representación textual de un ``ParseTree`` que hace explícitos
los bindings de cada hoja ``VALOR_*`` / ``N_COLUMNA``.  El objetivo no es
producir lenguaje natural perfecto sino **distinguir** dos lecturas que
compiten por el mismo lemma.

Ejemplo motivador (spec §4.3): "ventas de Juan" produce dos árboles:
  - VALOR_NOMBRE Juan -> binding (vendedores, nombre)
  - VALOR_NOMBRE Juan -> binding (clientes, nombre)
La paráfrasis los renderiza como
  "ventas POR el vendedor llamado Juan"  vs
  "ventas A el cliente llamado Juan",
permitiéndole al usuario escoger.

También provee:
  * ``record_choice(ctx, tree)`` — persiste los bindings del árbol elegido
    en ``ctx.bindings`` para sesgar futuras desambiguaciones (Capa 2 lo
    consulta vía ``context_bonus``).
  * ``context_bonus(tree, ctx)`` — bonus aditivo (+1) por cada binding del
    árbol que coincide con una elección previa registrada en ``ctx``.
"""

from __future__ import annotations

from typing import Iterable

from consultaES.lexicon import LexicalItem
from consultaES.parser.tree import ParseTree


# ---------------------------------------------------------------------------
# Mapas de plantillas
# ---------------------------------------------------------------------------

_INTERROG_MAP = {
    "cuántos": "Cuántos",
    "cuántas": "Cuántas",
    "qué": "Qué",
    "cuál": "Cuál",
    "cuáles": "Cuáles",
    "quién": "Quién",
    "quiénes": "Quiénes",
    "dónde": "Dónde",
    "cuándo": "Cuándo",
}

_IMPERATIVO_MAP = {
    "muéstrame": "Muéstrame los",
    "muestra": "Muestra los",
    "lista": "Lista los",
    "dame": "Dame los",
    "dime": "Dime los",
    "enseña": "Enseña los",
    "enseñame": "Enséñame los",
}

_AGG_MAP = {
    "total": "el total de",
    "suma": "la suma de",
    "promedio": "el promedio de",
    "media": "la media de",
    "cuenta": "la cantidad de",
    "cantidad": "la cantidad de",
    "máximo": "el máximo de",
    "mínimo": "el mínimo de",
}

# Plantilla de rol por (tabla, columna) para VALOR_NOMBRE.
_NOMBRE_ROLE = {
    ("vendedores", "nombre"): "el vendedor llamado",
    ("clientes", "nombre"): "el cliente llamado",
    ("productos", "nombre"): "el producto llamado",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_leaf(node) -> bool:
    return isinstance(node, LexicalItem)


def _join(parts: Iterable[str]) -> str:
    return " ".join(p for p in parts if p)


def _first_binding(leaf: LexicalItem) -> tuple[str, str | None] | None:
    if leaf.bindings:
        return leaf.bindings[0]
    return None


# ---------------------------------------------------------------------------
# Render de hojas terminales
# ---------------------------------------------------------------------------

def _render_leaf(leaf: LexicalItem) -> str:
    cat = leaf.category
    lemma = leaf.lemma

    if cat == "INTERROG":
        return _INTERROG_MAP.get(lemma.lower(), lemma)
    if cat == "IMPERATIVO":
        return _IMPERATIVO_MAP.get(lemma.lower(), lemma)
    if cat == "DET":
        return lemma
    if cat == "AGG":
        return _AGG_MAP.get(lemma.lower(), lemma)
    if cat == "PREP":
        return lemma
    if cat == "CONECTOR":
        return lemma
    if cat == "OP_COMP":
        return lemma
    if cat == "DIR":
        return lemma
    if cat == "AGR_MARKER":
        return "agrupados por"
    if cat == "ORD_MARKER":
        return "ordenados por"
    if cat == "N_TABLA":
        return f"los {lemma}"
    if cat == "N_COLUMNA":
        b = _first_binding(leaf)
        if b is not None:
            t, _c = b
            return f"el campo '{lemma}' de {t}"
        return f"el campo '{lemma}'"
    if cat == "VALOR_NOMBRE":
        b = _first_binding(leaf)
        if b is not None:
            tpl = _NOMBRE_ROLE.get(b)
            if tpl is not None:
                return f"{tpl} {lemma}"
            return f"{b[0]} llamado {lemma}"
        return f"llamado {lemma}"
    if cat == "VALOR_CIUDAD":
        return f"la ciudad de {lemma}"
    if cat == "VALOR_CATEGORIA":
        return f"la categoría '{lemma}'"
    if cat == "VALOR_TIPO":
        return f"el tipo '{lemma}'"
    if cat == "NUM":
        return str(lemma)
    if cat == "CADENA":
        return f"'{lemma}'"
    if cat == "FECHA":
        return f"la fecha {lemma}"
    # Default conservador: lemma plano.
    return str(lemma)


# ---------------------------------------------------------------------------
# Render de subárboles por etiqueta
# ---------------------------------------------------------------------------

def _render_children(node: ParseTree) -> list[str]:
    return [paraphrase(c) if isinstance(c, ParseTree) else _render_leaf(c)
            for c in node.children]


def _render_node(node: ParseTree) -> str:
    label = node.label
    children = node.children

    if label in ("S", "Pregunta", "Nucleo", "Cola"):
        return _join(_render_children(node))

    if label == "SN":
        # Caso típico: Det N_TABLA  -> "los <tabla>"; o sólo N_TABLA.
        # Como _render_leaf(N_TABLA) ya inyecta "los", evitamos doble det.
        parts: list[str] = []
        seen_det = False
        for c in children:
            if isinstance(c, LexicalItem):
                if c.category == "DET":
                    seen_det = True
                    parts.append(c.lemma)
                elif c.category == "N_TABLA":
                    if seen_det:
                        parts.append(c.lemma)
                    else:
                        parts.append(f"los {c.lemma}")
                elif c.category == "NUM":
                    parts.append(str(c.lemma))
                else:
                    parts.append(_render_leaf(c))
            else:
                parts.append(paraphrase(c))
        return _join(parts)

    if label == "Det":
        return _join(_render_children(node))

    if label == "Interrog" or label == "Imperativo":
        return _join(_render_children(node))

    if label == "Agregacion":
        # AGG PREP N_COLUMNA   o   AGG.
        agg_lemma = ""
        col_render = ""
        for c in children:
            if isinstance(c, LexicalItem):
                if c.category == "AGG":
                    agg_lemma = _AGG_MAP.get(c.lemma.lower(), c.lemma)
                elif c.category == "N_COLUMNA":
                    col_render = _render_leaf(c)
                # PREP omitida: ya está implícita en "el total DE …".
            else:
                col_render = paraphrase(c)
        return _join([agg_lemma, col_render])

    if label == "Agrupacion":
        # AGR_MARKER PREP N_COLUMNA
        col = next(
            (_render_leaf(c) for c in children
             if isinstance(c, LexicalItem) and c.category == "N_COLUMNA"),
            "",
        )
        return _join(["agrupados por", col])

    if label == "Orden":
        col = next(
            (_render_leaf(c) for c in children
             if isinstance(c, LexicalItem) and c.category == "N_COLUMNA"),
            "",
        )
        direction = ""
        for c in children:
            if isinstance(c, ParseTree) and c.label == "Direccion":
                direction = paraphrase(c)
            elif isinstance(c, LexicalItem) and c.category == "DIR":
                direction = c.lemma
        return _join(["ordenados por", col, direction])

    if label == "Direccion":
        return _join(_render_children(node))

    if label == "Filtros":
        # Filtro [CONECTOR Filtros]
        return _join(_render_children(node))

    if label == "Filtro":
        # PREP N_COLUMNA OP_COMP Valor  ->  "con <col> <op> <valor>"
        col = ""
        op = ""
        val = ""
        for c in children:
            if isinstance(c, LexicalItem):
                if c.category == "N_COLUMNA":
                    col = _render_leaf(c)
                elif c.category == "OP_COMP":
                    op = c.lemma
            elif isinstance(c, ParseTree):
                if c.label == "Valor":
                    val = paraphrase(c)
        return _join(["con", col, op, val])

    if label == "Valor":
        return _join(_render_children(node))

    # Fallback estructural: nunca crashear.
    return _join(_render_children(node))


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def paraphrase(tree) -> str:
    """Renderiza una paráfrasis en español de un ``ParseTree``.

    Total: nunca lanza.  Para etiquetas no contempladas hace una recursión
    estructural que une los hijos por espacios.
    """
    if tree is None:
        return ""
    if isinstance(tree, LexicalItem):
        return _render_leaf(tree)
    if isinstance(tree, ParseTree):
        try:
            return _render_node(tree)
        except Exception:
            # Fallback ultra-defensivo.
            try:
                return _join(
                    paraphrase(c) if isinstance(c, ParseTree)
                    else _render_leaf(c)
                    for c in tree.children
                )
            except Exception:
                return tree.label
    return str(tree)


# ---------------------------------------------------------------------------
# Memoria de elecciones del usuario
# ---------------------------------------------------------------------------

_VALUE_CATEGORIES = {"VALOR_NOMBRE", "VALOR_CIUDAD", "VALOR_CATEGORIA", "VALOR_TIPO"}


def _iter_value_leaves(node) -> Iterable[LexicalItem]:
    if isinstance(node, LexicalItem):
        if node.category in _VALUE_CATEGORIES:
            yield node
        return
    if isinstance(node, ParseTree):
        for c in node.children:
            yield from _iter_value_leaves(c)


def record_choice(ctx, tree: ParseTree) -> None:
    """Persiste en ``ctx.bindings`` los bindings de las hojas VALOR_* del árbol elegido.

    Sirve para que sucesivas consultas en la misma sesión usen ``context_bonus``
    y favorezcan la lectura previamente confirmada por el usuario.
    """
    if ctx is None or tree is None:
        return
    bindings = getattr(ctx, "bindings", None)
    if bindings is None:
        return
    for leaf in _iter_value_leaves(tree):
        b = _first_binding(leaf)
        if b is not None:
            bindings[leaf.lemma] = b


def context_bonus(tree: ParseTree, ctx) -> int:
    """+1 por cada hoja VALOR_* cuyo binding coincide con uno previamente
    registrado en ``ctx.bindings`` (misma elección que en una consulta
    anterior de la misma sesión).
    """
    if ctx is None or tree is None:
        return 0
    bindings = getattr(ctx, "bindings", None)
    if not bindings:
        return 0
    bonus = 0
    for leaf in _iter_value_leaves(tree):
        prev = bindings.get(leaf.lemma)
        if prev is None:
            continue
        b = _first_binding(leaf)
        if b is not None and tuple(b) == tuple(prev):
            bonus += 1
    return bonus


__all__ = ["paraphrase", "record_choice", "context_bonus"]
