from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from consultaES.disambiguator import Context, DisambiguationRequest, disambiguate
from consultaES.grammar import load_grammar
from consultaES.lexicon import LexicalItem, build_lexicon, categorize
from consultaES.parser import parse
from consultaES.parser.tree import ParseTree
from consultaES.semantics import interpret, prepare_sql_ast
from consultaES.sqlgen import generate
from consultaES.tokenizer import tokenize

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "data" / "schema.sql"
DB_PATH = ROOT / "data" / "tienda.db"
RULES_PATH = ROOT / "src" / "consultaES" / "grammar" / "rules.cfg"


def norm(sql: str) -> str:
    """Normaliza SQL: minusculas y espacios colapsados."""
    return re.sub(r"\s+", " ", sql.lower()).strip()


@dataclass(frozen=True)
class GoldenCase:
    pregunta: str
    sql_esperado: str
    filas_esperadas: list[tuple]
    categorias: set[str] = field(default_factory=set)
    forced_choice: tuple[str, str] | None = None


def _leaves(node) -> list[LexicalItem]:
    if isinstance(node, LexicalItem):
        return [node]
    if isinstance(node, ParseTree):
        leaves: list[LexicalItem] = []
        for child in node.children:
            leaves.extend(_leaves(child))
        return leaves
    return []


def _has_binding(tree: ParseTree, binding: tuple[str, str]) -> bool:
    return any(binding in leaf.bindings for leaf in _leaves(tree))


def _resolve_tree(trees: list[ParseTree], case: GoldenCase, lex) -> ParseTree:
    result = disambiguate(trees, lex, Context(), db_path=str(DB_PATH))

    if case.forced_choice is None:
        assert not isinstance(result, DisambiguationRequest), (
            f"{case.pregunta!r} disparo capa 3 sin forced_choice"
        )
        assert isinstance(result, ParseTree)
        return result

    assert isinstance(result, DisambiguationRequest), (
        f"{case.pregunta!r} debia disparar capa 3 para usar forced_choice"
    )
    matches = [
        option.tree
        for option in result.options
        if _has_binding(option.tree, case.forced_choice)
    ]
    assert matches, (
        f"forced_choice={case.forced_choice!r} no existe entre "
        f"{[option.paraphrase for option in result.options]!r}"
    )
    return matches[0]


@pytest.fixture(scope="module")
def rig():
    lex = build_lexicon(str(SCHEMA_PATH), str(DB_PATH))
    grammar = load_grammar(str(RULES_PATH))
    return lex, grammar


WHERE_SIMPLE = "where_simple"
AGG_GROUP = "agg_group"
JOIN_IMPLICITO = "join_implicito"
ORDER_LIMIT = "order_limit"
CAPA2 = "capa2_ranking"
CAPA3 = "capa3_forced"
AGG_SIMPLE = "agg_simple"
LIMIT_SIMPLE = "limit_simple"


CORPUS = [
    GoldenCase(
        "lista los productos con precio menor que 50000",
        "select productos.* from productos where precio < ?",
        [
            (5, "Cargador USB-C", "Electrónica", 45000.0),
            (15, "Novela colombiana", "Libros", 38000.0),
            (17, "Libro de cocina", "Libros", 44000.0),
        ],
        {WHERE_SIMPLE},
    ),
    GoldenCase(
        "muéstrame los vendedores con ciudad igual a 'Cali'",
        "select vendedores.* from vendedores where ciudad = ?",
        [(3, "Andrés", "Cali", "2021-09-10"), (5, "Luisa", "Cali", "2019-11-05")],
        {WHERE_SIMPLE},
    ),
    GoldenCase(
        "lista los clientes con nombre igual a 'Juan'",
        "select clientes.* from clientes where nombre = ?",
        [(3, "Juan", "Cali", "2020-11-03", "premium")],
        {WHERE_SIMPLE},
    ),
    GoldenCase(
        "muéstrame los pedidos con total mayor que 1000000",
        "select pedidos.* from pedidos where total > ?",
        [(66, 14, 4, "2024-11-29", 1100000.0), (69, 19, 7, "2024-12-20", 1350000.0)],
        {WHERE_SIMPLE},
    ),
    GoldenCase(
        "muéstrame los pedidos con total menor que 100000",
        "select pedidos.* from pedidos where total < ?",
        [(6, 18, 5, "2024-03-11", 95000.0), (27, 5, 8, "2024-01-22", 90000.0)],
        {WHERE_SIMPLE},
    ),
    GoldenCase(
        "lista los productos con categoria igual a 'Electrónica'",
        "select productos.* from productos where categoria = ?",
        [
            (1, "Teclado", "Electrónica", 120000.0),
            (2, "Mouse inalámbrico", "Electrónica", 85000.0),
            (3, 'Monitor 24"', "Electrónica", 750000.0),
            (4, "Audífonos Bluetooth", "Electrónica", 220000.0),
            (5, "Cargador USB-C", "Electrónica", 45000.0),
        ],
        {WHERE_SIMPLE},
    ),
    GoldenCase(
        "muéstrame los productos con precio mayor que 700000",
        "select productos.* from productos where precio > ?",
        [(3, 'Monitor 24"', "Electrónica", 750000.0)],
        {WHERE_SIMPLE},
    ),
    GoldenCase(
        "muéstrame los clientes con tipo igual a 'premium'",
        "select clientes.* from clientes where tipo = ?",
        [
            (2, "Carlos", "Medellín", "2021-08-22", "premium"),
            (3, "Juan", "Cali", "2020-11-03", "premium"),
            (6, "Sofía", "Bogotá", "2021-03-28", "premium"),
            (8, "Diego", "Cali", "2020-09-04", "premium"),
            (11, "Daniela", "Cali", "2023-08-29", "premium"),
            (13, "Isabella", "Bogotá", "2022-10-05", "premium"),
            (16, "Santiago", "Medellín", "2022-09-08", "premium"),
            (19, "Mariana", "Barranquilla", "2023-04-06", "premium"),
            (21, "Gabriela", "Medellín", "2021-06-09", "premium"),
            (23, "Natalia", "Barranquilla", "2020-12-28", "premium"),
        ],
        {WHERE_SIMPLE},
    ),
    GoldenCase(
        "cuenta de clientes agrupados por ciudad",
        "select count(*) from clientes group by ciudad",
        [(5,), (6,), (7,), (5,)],
        {AGG_GROUP},
    ),
    GoldenCase(
        "cuenta de clientes agrupados por tipo",
        "select count(*) from clientes group by tipo",
        [(10,), (13,)],
        {AGG_GROUP},
    ),
    GoldenCase(
        "mínimo de precio de productos agrupados por categoria",
        "select min(productos.precio) from productos group by categoria",
        [(65000.0,), (45000.0,), (95000.0,), (38000.0,), (55000.0,)],
        {AGG_GROUP},
    ),
    GoldenCase(
        "máximo de precio de productos agrupados por categoria",
        "select max(productos.precio) from productos group by categoria",
        [(280000.0,), (750000.0,), (195000.0,), (52000.0,), (180000.0,)],
        {AGG_GROUP},
    ),
    GoldenCase(
        "promedio de precio de productos agrupados por categoria",
        "select avg(productos.precio) from productos group by categoria",
        [
            (145000.0,),
            (244000.0,),
            (136666.66666666666,),
            (44666.666666666664,),
            (121666.66666666667,),
        ],
        {AGG_GROUP},
    ),
    GoldenCase(
        "cuenta de productos agrupados por categoria",
        "select count(*) from productos group by categoria",
        [(3,), (5,), (3,), (3,), (3,)],
        {AGG_GROUP},
    ),
    GoldenCase(
        "muéstrame los 5 productos ordenados por precio descendente",
        "select productos.* from productos order by precio desc limit 5",
        [
            (3, 'Monitor 24"', "Electrónica", 750000.0),
            (9, "Zapatillas running", "Deportes", 280000.0),
            (4, "Audífonos Bluetooth", "Electrónica", 220000.0),
            (13, "Cafetera eléctrica", "Hogar", 195000.0),
            (7, "Chaqueta impermeable", "Ropa", 180000.0),
        ],
        {ORDER_LIMIT},
    ),
    GoldenCase(
        "muéstrame los 3 pedidos ordenados por total descendente",
        "select pedidos.* from pedidos order by total desc limit 3",
        [
            (69, 19, 7, "2024-12-20", 1350000.0),
            (66, 14, 4, "2024-11-29", 1100000.0),
            (110, 2, 8, "2025-06-13", 980000.0),
        ],
        {ORDER_LIMIT},
    ),
    GoldenCase(
        "muéstrame los 4 clientes ordenados por nombre ascendente",
        "select clientes.* from clientes order by nombre asc limit 4",
        [
            (17, "Alejandra", "Bogotá", "2021-11-30", "regular"),
            (5, "Andrés", "Barranquilla", "2022-07-19", "regular"),
            (9, "Camila", "Barranquilla", "2022-12-01", "regular"),
            (2, "Carlos", "Medellín", "2021-08-22", "premium"),
        ],
        {ORDER_LIMIT},
    ),
    GoldenCase(
        "muéstrame los 5 vendedores ordenados por ciudad",
        "select vendedores.* from vendedores order by ciudad asc limit 5",
        [
            (6, "Carlos", "Barranquilla", "2020-04-18"),
            (8, "Sebastián", "Barranquilla", "2018-06-30"),
            (4, "Camila", "Bogotá", "2022-01-20"),
            (7, "Natalia", "Bogotá", "2023-02-14"),
            (3, "Andrés", "Cali", "2021-09-10"),
        ],
        {ORDER_LIMIT},
    ),
    GoldenCase(
        "ventas de Juan",
        "select pedidos.* from pedidos join clientes on pedidos.id_cliente = clientes.id "
        "where clientes.nombre = ?",
        [
            (1, 3, 2, "2024-03-02", 250000.0),
            (8, 3, 1, "2024-03-14", 450000.0),
            (15, 3, 5, "2024-03-22", 250000.0),
            (22, 3, 1, "2024-03-29", 680000.0),
            (80, 3, 2, "2025-03-01", 480000.0),
            (87, 3, 1, "2025-03-15", 620000.0),
            (94, 3, 5, "2025-03-26", 920000.0),
        ],
        {JOIN_IMPLICITO, CAPA3},
        forced_choice=("clientes", "nombre"),
    ),
    GoldenCase(
        "ventas de Cali",
        "select pedidos.* from pedidos join clientes on pedidos.id_cliente = clientes.id "
        "where clientes.ciudad = ?",
        [
            (1, 3, 2, "2024-03-02", 250000.0),
            (2, 4, 2, "2024-03-05", 180000.0),
            (3, 8, 2, "2024-03-07", 550000.0),
            (4, 11, 2, "2024-03-09", 220000.0),
            (5, 15, 3, "2024-03-10", 130000.0),
            (6, 18, 5, "2024-03-11", 95000.0),
            (7, 22, 2, "2024-03-12", 320000.0),
            (8, 3, 1, "2024-03-14", 450000.0),
            (9, 4, 3, "2024-03-15", 280000.0),
            (10, 8, 5, "2024-03-17", 190000.0),
            (11, 11, 2, "2024-03-18", 660000.0),
            (12, 15, 1, "2024-03-19", 120000.0),
            (13, 18, 3, "2024-03-20", 385000.0),
            (14, 22, 2, "2024-03-21", 510000.0),
            (15, 3, 5, "2024-03-22", 250000.0),
            (16, 4, 2, "2024-03-23", 870000.0),
            (17, 8, 1, "2024-03-24", 430000.0),
            (18, 11, 3, "2024-03-25", 290000.0),
            (19, 15, 2, "2024-03-26", 145000.0),
            (20, 18, 5, "2024-03-27", 530000.0),
            (21, 22, 2, "2024-03-28", 210000.0),
            (22, 3, 1, "2024-03-29", 680000.0),
            (23, 4, 3, "2024-03-30", 350000.0),
            (24, 8, 2, "2024-03-31", 120000.0),
            (80, 3, 2, "2025-03-01", 480000.0),
            (81, 4, 2, "2025-03-03", 220000.0),
            (82, 8, 2, "2025-03-05", 350000.0),
            (83, 11, 2, "2025-03-07", 590000.0),
            (84, 15, 3, "2025-03-09", 140000.0),
            (85, 18, 5, "2025-03-11", 270000.0),
            (86, 22, 2, "2025-03-13", 415000.0),
            (87, 3, 1, "2025-03-15", 620000.0),
            (88, 4, 3, "2025-03-17", 195000.0),
            (89, 8, 5, "2025-03-19", 510000.0),
            (90, 11, 2, "2025-03-21", 330000.0),
            (91, 15, 1, "2025-03-23", 250000.0),
            (92, 18, 3, "2025-03-24", 680000.0),
            (93, 22, 2, "2025-03-25", 175000.0),
            (94, 3, 5, "2025-03-26", 920000.0),
            (95, 4, 2, "2025-03-27", 340000.0),
            (96, 8, 1, "2025-03-28", 460000.0),
            (97, 11, 3, "2025-03-29", 285000.0),
            (98, 15, 2, "2025-03-30", 730000.0),
            (99, 18, 5, "2025-03-31", 190000.0),
        ],
        {JOIN_IMPLICITO, CAPA3},
        forced_choice=("clientes", "ciudad"),
    ),
    GoldenCase(
        "ventas de Bogotá",
        "select pedidos.* from pedidos join clientes on pedidos.id_cliente = clientes.id "
        "where clientes.ciudad = ?",
        [
            (25, 1, 4, "2024-01-08", 310000.0),
            (28, 6, 4, "2024-02-03", 780000.0),
            (31, 10, 4, "2024-02-25", 130000.0),
            (33, 13, 4, "2024-04-12", 880000.0),
            (36, 17, 4, "2024-05-03", 420000.0),
            (38, 20, 8, "2024-05-17", 185000.0),
            (41, 1, 6, "2024-06-07", 495000.0),
            (44, 6, 7, "2024-06-28", 350000.0),
            (47, 10, 8, "2024-07-19", 145000.0),
            (49, 13, 6, "2024-08-02", 290000.0),
            (52, 17, 7, "2024-08-23", 195000.0),
            (54, 20, 6, "2024-09-06", 440000.0),
            (57, 1, 7, "2024-09-27", 260000.0),
            (60, 6, 8, "2024-10-18", 740000.0),
            (63, 10, 6, "2024-11-08", 650000.0),
            (65, 13, 7, "2024-11-22", 295000.0),
            (68, 17, 8, "2024-12-13", 420000.0),
            (70, 20, 4, "2024-12-27", 290000.0),
            (73, 1, 4, "2025-01-17", 640000.0),
            (76, 6, 4, "2025-02-07", 790000.0),
            (79, 10, 4, "2025-02-28", 300000.0),
            (101, 13, 4, "2025-04-11", 870000.0),
            (104, 17, 4, "2025-05-02", 680000.0),
            (106, 20, 8, "2025-05-16", 830000.0),
            (109, 1, 6, "2025-06-06", 360000.0),
        ],
        {JOIN_IMPLICITO, CAPA3},
        forced_choice=("clientes", "ciudad"),
    ),
    GoldenCase(
        "ventas de Pedro",
        "select pedidos.* from pedidos join vendedores on pedidos.id_vendedor = vendedores.id "
        "where vendedores.nombre = ?",
        [
            (1, 3, 2, "2024-03-02", 250000.0),
            (2, 4, 2, "2024-03-05", 180000.0),
            (3, 8, 2, "2024-03-07", 550000.0),
            (4, 11, 2, "2024-03-09", 220000.0),
            (7, 22, 2, "2024-03-12", 320000.0),
            (11, 11, 2, "2024-03-18", 660000.0),
            (14, 22, 2, "2024-03-21", 510000.0),
            (16, 4, 2, "2024-03-23", 870000.0),
            (19, 15, 2, "2024-03-26", 145000.0),
            (21, 22, 2, "2024-03-28", 210000.0),
            (24, 8, 2, "2024-03-31", 120000.0),
            (80, 3, 2, "2025-03-01", 480000.0),
            (81, 4, 2, "2025-03-03", 220000.0),
            (82, 8, 2, "2025-03-05", 350000.0),
            (83, 11, 2, "2025-03-07", 590000.0),
            (86, 22, 2, "2025-03-13", 415000.0),
            (90, 11, 2, "2025-03-21", 330000.0),
            (93, 22, 2, "2025-03-25", 175000.0),
            (95, 4, 2, "2025-03-27", 340000.0),
            (98, 15, 2, "2025-03-30", 730000.0),
        ],
        {JOIN_IMPLICITO},
    ),
    GoldenCase(
        "ventas de Carlos",
        "select pedidos.* from pedidos join vendedores on pedidos.id_vendedor = vendedores.id "
        "where vendedores.nombre = ?",
        [
            (26, 2, 6, "2024-01-15", 450000.0),
            (30, 9, 6, "2024-02-18", 240000.0),
            (37, 19, 6, "2024-05-10", 750000.0),
            (41, 1, 6, "2024-06-07", 495000.0),
            (45, 7, 6, "2024-07-05", 230000.0),
            (49, 13, 6, "2024-08-02", 290000.0),
            (54, 20, 6, "2024-09-06", 440000.0),
            (58, 2, 6, "2024-10-04", 920000.0),
            (63, 10, 6, "2024-11-08", 650000.0),
            (67, 16, 6, "2024-12-06", 580000.0),
            (71, 21, 6, "2025-01-03", 510000.0),
            (75, 5, 6, "2025-01-31", 225000.0),
            (100, 12, 6, "2025-04-04", 550000.0),
            (105, 19, 6, "2025-05-09", 145000.0),
            (109, 1, 6, "2025-06-06", 360000.0),
        ],
        {JOIN_IMPLICITO, CAPA2},
    ),
    GoldenCase(
        "ventas de Andrés",
        "select pedidos.* from pedidos join vendedores on pedidos.id_vendedor = vendedores.id "
        "where vendedores.nombre = ?",
        [
            (5, 15, 3, "2024-03-10", 130000.0),
            (9, 4, 3, "2024-03-15", 280000.0),
            (13, 18, 3, "2024-03-20", 385000.0),
            (18, 11, 3, "2024-03-25", 290000.0),
            (23, 4, 3, "2024-03-30", 350000.0),
            (84, 15, 3, "2025-03-09", 140000.0),
            (88, 4, 3, "2025-03-17", 195000.0),
            (92, 18, 3, "2025-03-24", 680000.0),
            (97, 11, 3, "2025-03-29", 285000.0),
        ],
        {JOIN_IMPLICITO, CAPA2},
    ),
    GoldenCase(
        "ventas de Camila",
        "select pedidos.* from pedidos join vendedores on pedidos.id_vendedor = vendedores.id "
        "where vendedores.nombre = ?",
        [
            (25, 1, 4, "2024-01-08", 310000.0),
            (28, 6, 4, "2024-02-03", 780000.0),
            (31, 10, 4, "2024-02-25", 130000.0),
            (33, 13, 4, "2024-04-12", 880000.0),
            (36, 17, 4, "2024-05-03", 420000.0),
            (39, 21, 4, "2024-05-24", 630000.0),
            (43, 5, 4, "2024-06-21", 810000.0),
            (46, 9, 4, "2024-07-12", 670000.0),
            (50, 14, 4, "2024-08-09", 720000.0),
            (53, 19, 4, "2024-08-30", 860000.0),
            (56, 23, 4, "2024-09-20", 580000.0),
            (59, 5, 4, "2024-10-11", 170000.0),
            (62, 9, 4, "2024-11-01", 210000.0),
            (66, 14, 4, "2024-11-29", 1100000.0),
            (70, 20, 4, "2024-12-27", 290000.0),
            (73, 1, 4, "2025-01-17", 640000.0),
            (76, 6, 4, "2025-02-07", 790000.0),
            (79, 10, 4, "2025-02-28", 300000.0),
            (101, 13, 4, "2025-04-11", 870000.0),
            (104, 17, 4, "2025-05-02", 680000.0),
            (107, 21, 4, "2025-05-23", 270000.0),
        ],
        {JOIN_IMPLICITO, CAPA2},
    ),
    GoldenCase(
        "ventas de Natalia",
        "select pedidos.* from pedidos join vendedores on pedidos.id_vendedor = vendedores.id "
        "where vendedores.nombre = ?",
        [
            (29, 7, 7, "2024-02-10", 165000.0),
            (32, 12, 7, "2024-04-05", 560000.0),
            (35, 16, 7, "2024-04-26", 340000.0),
            (40, 23, 7, "2024-05-31", 270000.0),
            (44, 6, 7, "2024-06-28", 350000.0),
            (48, 12, 7, "2024-07-26", 540000.0),
            (52, 17, 7, "2024-08-23", 195000.0),
            (57, 1, 7, "2024-09-27", 260000.0),
            (61, 7, 7, "2024-10-25", 330000.0),
            (65, 13, 7, "2024-11-22", 295000.0),
            (69, 19, 7, "2024-12-20", 1350000.0),
            (74, 2, 7, "2025-01-24", 380000.0),
            (78, 9, 7, "2025-02-21", 430000.0),
            (103, 16, 7, "2025-04-25", 395000.0),
            (108, 23, 7, "2025-05-30", 510000.0),
        ],
        {JOIN_IMPLICITO, CAPA2},
    ),
    GoldenCase(
        "cuenta de clientes",
        "select count(*) from clientes",
        [(23,)],
        {AGG_SIMPLE},
    ),
    GoldenCase(
        "suma de total de pedidos",
        "select sum(pedidos.total) from pedidos",
        [(47100000.0,)],
        {AGG_SIMPLE},
    ),
    GoldenCase(
        "promedio de precio de productos",
        "select avg(productos.precio) from productos",
        [(150823.5294117647,)],
        {AGG_SIMPLE},
    ),
    GoldenCase(
        "máximo de total de pedidos",
        "select max(pedidos.total) from pedidos",
        [(1350000.0,)],
        {AGG_SIMPLE},
    ),
    GoldenCase(
        "mínimo de total de pedidos",
        "select min(pedidos.total) from pedidos",
        [(90000.0,)],
        {AGG_SIMPLE},
    ),
    GoldenCase(
        "muéstrame los 3 productos",
        "select productos.* from productos limit 3",
        [
            (1, "Teclado", "Electrónica", 120000.0),
            (2, "Mouse inalámbrico", "Electrónica", 85000.0),
            (3, 'Monitor 24"', "Electrónica", 750000.0),
        ],
        {LIMIT_SIMPLE},
    ),
    GoldenCase(
        "muéstrame los 2 clientes",
        "select clientes.* from clientes limit 2",
        [
            (1, "Laura", "Bogotá", "2022-05-10", "regular"),
            (2, "Carlos", "Medellín", "2021-08-22", "premium"),
        ],
        {LIMIT_SIMPLE},
    ),
    GoldenCase(
        "muéstrame los 2 vendedores",
        "select vendedores.* from vendedores limit 2",
        [(1, "Juan", "Medellín", "2021-03-15"), (2, "Pedro", "Medellín", "2020-07-01")],
        {LIMIT_SIMPLE},
    ),
]


def _case_id(case: GoldenCase) -> str:
    return case.pregunta.replace(" ", "-").replace("'", "").lower()


@pytest.mark.parametrize("case", CORPUS, ids=_case_id)
def test_golden_corpus_sql_y_filas(case: GoldenCase, rig):
    lex, grammar = rig
    tokens = tokenize(case.pregunta)
    items = categorize(tokens, lex)
    trees = parse(items, grammar)
    assert trees, f"no parse for: {case.pregunta}"
    if CAPA2 in case.categorias:
        assert len(trees) > 1

    tree = _resolve_tree(trees, case, lex)
    ast = prepare_sql_ast(interpret(tree), lex)
    sql, rows = generate(ast, db=str(DB_PATH), execute=True)

    assert norm(sql) == case.sql_esperado
    assert rows == case.filas_esperadas


def test_corpus_cubre_categorias_task_6_3():
    assert len(CORPUS) >= 30
    assert sum(WHERE_SIMPLE in case.categorias for case in CORPUS) >= 8
    assert sum(AGG_GROUP in case.categorias for case in CORPUS) >= 6
    assert sum(JOIN_IMPLICITO in case.categorias for case in CORPUS) >= 5
    assert sum(ORDER_LIMIT in case.categorias for case in CORPUS) >= 4
    assert sum(CAPA2 in case.categorias for case in CORPUS) >= 4
    assert sum(CAPA3 in case.categorias for case in CORPUS) >= 3
