"""Resolución automática de JOINs usando el grafo de foreign keys del lexicon."""

from __future__ import annotations

from collections import deque

from consultaES.lexicon import Lexicon
from consultaES.semantics.ast import Column, Join, SQLAst


def _collect_tables(ast: SQLAst) -> set[str]:
    """Recolecta todas las tablas referenciadas en el AST."""
    tables: set[str] = set()

    # tables explícitas
    tables.update(ast.tables)

    # SELECT
    for col in ast.select:
        if col.table:
            tables.add(col.table)

    # WHERE
    for _, cond in ast.where:
        if cond.col.table:
            tables.add(cond.col.table)

    # GROUP BY
    for col in ast.group_by:
        if col.table:
            tables.add(col.table)

    # HAVING
    for _, cond in ast.having:
        if cond.col.table:
            tables.add(cond.col.table)

    # ORDER BY
    for col, _ in ast.order_by:
        if col.table:
            tables.add(col.table)

    return tables


def _build_fk_graph(fks: dict[tuple[str, str], tuple[str, str]]) -> dict[str, list[tuple[str, str, str, str, str]]]:
    """Construye un grafo bidireccional de tablas conectadas por FKs.

    Retorna: {tabla: [(tabla_vecina, src_table, src_col, dst_table, dst_col), ...]}
    Cada arista se guarda en ambas direcciones con la info FK original.
    """
    graph: dict[str, list[tuple[str, str, str, str, str]]] = {}

    for (src_table, src_col), (dst_table, dst_col) in fks.items():
        # Dirección src -> dst
        graph.setdefault(src_table, []).append(
            (dst_table, src_table, src_col, dst_table, dst_col)
        )
        # Dirección dst -> src
        graph.setdefault(dst_table, []).append(
            (src_table, src_table, src_col, dst_table, dst_col)
        )

    return graph


def _find_path_bfs(
    graph: dict[str, list[tuple[str, str, str, str, str]]],
    start: str,
    target: str,
) -> list[tuple[str, str, str, str]]:
    """BFS para encontrar el camino más corto entre dos tablas.

    Retorna lista de (src_table, src_col, dst_table, dst_col) en orden.
    """
    if start == target:
        return []

    visited: set[str] = {start}
    # cola: (nodo_actual, camino_de_aristas)
    queue: deque[tuple[str, list[tuple[str, str, str, str]]]] = deque()
    queue.append((start, []))

    while queue:
        current, path = queue.popleft()
        for neighbor, src_t, src_c, dst_t, dst_c in graph.get(current, []):
            if neighbor in visited:
                continue
            edge = (src_t, src_c, dst_t, dst_c)
            new_path = path + [edge]
            if neighbor == target:
                return new_path
            visited.add(neighbor)
            queue.append((neighbor, new_path))

    return []  # No hay camino


def resolve_joins(ast: SQLAst, lexicon: Lexicon) -> SQLAst:
    """Resuelve JOINs automáticamente basándose en las FKs del lexicon.

    Dado un AST con columnas de múltiples tablas, inserta los JOIN
    necesarios usando BFS sobre el grafo de foreign keys.
    """
    referenced = _collect_tables(ast)

    # Si solo hay una tabla (o ninguna), no hay nada que resolver
    if len(referenced) <= 1:
        return ast

    graph = _build_fk_graph(lexicon.fks)

    # Tabla principal: la primera en ast.tables
    main_table = ast.tables[0] if ast.tables else next(iter(referenced))

    # Tablas a conectar (todas menos la principal)
    targets = referenced - {main_table}

    # Recolectar todas las aristas necesarias (evitar duplicados)
    seen_edges: set[tuple[str, str, str, str]] = set()
    joins: list[Join] = []
    # También rastrear tablas ya conectadas para agregar intermedias
    connected: set[str] = {main_table}

    for target in sorted(targets):  # sorted para determinismo
        path = _find_path_bfs(graph, main_table, target)
        if not path:
            continue

        for src_t, src_c, dst_t, dst_c in path:
            edge_key = (src_t, src_c, dst_t, dst_c)
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)

            # Determinar cuál tabla es la nueva (la que se une)
            # La tabla que ya está conectada es la "izquierda"
            if src_t in connected:
                join_table = dst_t
                on_left = Column(src_t, src_c)
                on_right = Column(dst_t, dst_c)
            else:
                join_table = src_t
                on_left = Column(dst_t, dst_c)
                on_right = Column(src_t, src_c)

            joins.append(Join(table=join_table, on_left=on_left, on_right=on_right))
            connected.add(join_table)

    ast.joins = joins
    ast.tables = [main_table]
    return ast
