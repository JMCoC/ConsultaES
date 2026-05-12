from dataclasses import dataclass, field


@dataclass
class Column:
    table: str | None
    name: str
    agg: str | None = None


@dataclass
class Condition:
    col: Column
    op: str
    value: object
    negated: bool = False


@dataclass
class SQLAst:
    select: list = field(default_factory=list)
    tables: list = field(default_factory=list)
    where: list = field(default_factory=list)
    group_by: list = field(default_factory=list)
    having: list = field(default_factory=list)
    order_by: list = field(default_factory=list)
    limit: int | None = None


def interpret(tree) -> SQLAst:
    raise NotImplementedError
