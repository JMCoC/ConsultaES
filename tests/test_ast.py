import pytest
from consultaES.semantics.ast import Column, Condition, SQLAst

class TestColumn:
    def test_construccion_basica(self):
        col = Column(table="clientes", name="ciudad")
        assert col.table == "clientes"
        assert col.name == "ciudad"
        assert col.agg is None

    def test_columna_con_agregacion(self):
        col = Column(table="ventas", name="monto", agg="SUM")
        assert col.agg == "SUM"

    def test_columna_count_estrella(self):
        col = Column(table="", name="*", agg="COUNT")
        assert col.agg == "COUNT"
        assert col.name == "*"

    def test_todas_las_agregaciones(self):
        for agg in ("SUM", "COUNT", "AVG", "MIN", "MAX"):
            col = Column(table="t", name="n", agg=agg)
            assert col.agg == agg

    def test_igualdad_de_columnas(self):
        c1 = Column(table="clientes", name="ciudad")
        c2 = Column(table="clientes", name="ciudad")
        assert c1 == c2

    def test_columnas_distintas(self):
        c1 = Column(table="clientes", name="ciudad")
        c2 = Column(table="clientes", name="nombre")
        assert c1 != c2


class TestCondition:
    def test_construccion_basica(self):
        col = Column(table="clientes", name="ciudad")
        cond = Condition(col=col, op="=", value="Cali")
        assert cond.col == col
        assert cond.op == "="
        assert cond.value == "Cali"
        assert cond.negated is False

    def test_condicion_negada(self):
        col = Column(table="clientes", name="ciudad")
        cond = Condition(col=col, op="=", value="Cali", negated=True)
        assert cond.negated is True

    def test_operadores_comparacion(self):
        col = Column(table="ventas", name="monto")
        for op in ("=", "!=", "<", "<=", ">", ">="):
            cond = Condition(col=col, op=op, value=100)
            assert cond.op == op

    def test_operador_like(self):
        col = Column(table="clientes", name="nombre")
        cond = Condition(col=col, op="LIKE", value="%Juan%")
        assert cond.op == "LIKE"
        assert cond.value == "%Juan%"

    def test_operador_between(self):
        col = Column(table="ventas", name="fecha")
        cond = Condition(col=col, op="BETWEEN", value=("2025-01-01", "2025-12-31"))
        assert cond.op == "BETWEEN"
        assert cond.value == ("2025-01-01", "2025-12-31")

    def test_operador_in(self):
        col = Column(table="clientes", name="ciudad")
        cond = Condition(col=col, op="IN", value=["Cali", "Bogotá", "Medellín"])
        assert cond.op == "IN"
        assert len(cond.value) == 3

    def test_valor_numerico(self):
        col = Column(table="ventas", name="monto")
        cond = Condition(col=col, op=">", value=500.0)
        assert cond.value == 500.0


class TestSQLAstDefaults:
    def test_ast_vacio(self):
        ast = SQLAst()
        assert ast.select == []
        assert ast.tables == []
        assert ast.where == []
        assert ast.group_by == []
        assert ast.having == []
        assert ast.order_by == []
        assert ast.limit is None

    def test_instancias_independientes(self):
        ast1 = SQLAst()
        ast2 = SQLAst()
        ast1.tables.append("clientes")
        assert ast2.tables == []

class TestRoundtripSelectWhere:
    def _construir_ast(self):
        col_estrella = Column(table="clientes", name="*")
        cond = Condition(
            col=Column(table="clientes", name="ciudad"),
            op="=",
            value="Cali",
        )
        ast = SQLAst(
            select=[col_estrella],
            tables=["clientes"],
            where=[("", cond)],
        )
        return ast

    def test_select_tiene_una_columna(self):
        ast = self._construir_ast()
        assert len(ast.select) == 1
        assert ast.select[0].name == "*"
        assert ast.select[0].table == "clientes"

    def test_tabla_correcta(self):
        ast = self._construir_ast()
        assert ast.tables == ["clientes"]

    def test_where_tiene_una_condicion(self):
        ast = self._construir_ast()
        assert len(ast.where) == 1

    def test_primer_conector_es_vacio(self):
        ast = self._construir_ast()
        conector, _ = ast.where[0]
        assert conector == ""

    def test_condicion_correcta(self):
        ast = self._construir_ast()
        _, cond = ast.where[0]
        assert cond.col.name == "ciudad"
        assert cond.op == "="
        assert cond.value == "Cali"
        assert cond.negated is False

    def test_campos_sin_uso_son_vacios(self):
        ast = self._construir_ast()
        assert ast.group_by == []
        assert ast.having == []
        assert ast.order_by == []
        assert ast.limit is None

class TestAgregacion:
    def _construir_ast_count(self):
        col_count = Column(table="ventas", name="*", agg="COUNT")
        col_grupo = Column(table="ventas", name="vendedor_id")
        ast = SQLAst(
            select=[col_count],
            tables=["ventas"],
            group_by=[col_grupo],
        )
        return ast

    def test_select_con_count(self):
        ast = self._construir_ast_count()
        assert len(ast.select) == 1
        assert ast.select[0].agg == "COUNT"
        assert ast.select[0].name == "*"

    def test_group_by_presente(self):
        ast = self._construir_ast_count()
        assert len(ast.group_by) == 1
        assert ast.group_by[0].name == "vendedor_id"

    def test_where_vacio(self):
        ast = self._construir_ast_count()
        assert ast.where == []

    def test_having_con_agregacion(self):
        col_count = Column(table="ventas", name="*", agg="COUNT")
        col_grupo = Column(table="ventas", name="vendedor_id")
        cond_having = Condition(
            col=Column(table="ventas", name="*", agg="COUNT"),
            op=">",
            value=5,
        )
        ast = SQLAst(
            select=[col_count],
            tables=["ventas"],
            group_by=[col_grupo],
            having=[("", cond_having)],
        )
        assert len(ast.having) == 1
        _, cond = ast.having[0]
        assert cond.op == ">"
        assert cond.value == 5


class TestOrderByLimit:
    def test_order_by_desc(self):
        col = Column(table="clientes", name="nombre")
        ast = SQLAst(
            select=[col],
            tables=["clientes"],
            order_by=[(col, "DESC")],
            limit=10,
        )
        assert len(ast.order_by) == 1
        col_ord, direccion = ast.order_by[0]
        assert col_ord.name == "nombre"
        assert direccion == "DESC"
        assert ast.limit == 10

    def test_order_by_asc(self):
        col = Column(table="ventas", name="monto")
        ast = SQLAst(
            select=[col],
            tables=["ventas"],
            order_by=[(col, "ASC")],
        )
        _, direccion = ast.order_by[0]
        assert direccion == "ASC"


class TestCondicionesMultiples:
    def test_where_con_and(self):
        cond1 = Condition(
            col=Column(table="clientes", name="ciudad"),
            op="=",
            value="Cali",
        )
        cond2 = Condition(
            col=Column(table="ventas", name="monto"),
            op=">",
            value=100,
        )
        ast = SQLAst(
            select=[Column(table="clientes", name="*")],
            tables=["clientes", "ventas"],
            where=[("", cond1), ("AND", cond2)],
        )
        assert len(ast.where) == 2
        assert ast.where[0][0] == ""
        assert ast.where[1][0] == "AND"

    def test_where_con_or(self):
        col = Column(table="clientes", name="ciudad")
        cond1 = Condition(col=col, op="=", value="Cali")
        cond2 = Condition(col=col, op="=", value="Bogotá")
        ast = SQLAst(
            select=[Column(table="clientes", name="*")],
            tables=["clientes"],
            where=[("", cond1), ("OR", cond2)],
        )
        assert ast.where[1][0] == "OR"

    def test_join_implicito_dos_tablas(self): 
        ast = SQLAst(
            select=[Column(table="clientes", name="nombre")],
            tables=["clientes", "ventas"],
            where=[
                ("", Condition(
                    col=Column(table="clientes", name="id"),
                    op="=",
                    value=Column(table="ventas", name="cliente_id"),
                ))
            ],
        )
        assert "clientes" in ast.tables
        assert "ventas" in ast.tables
