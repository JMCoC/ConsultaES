from dataclasses import dataclass, field


@dataclass
class Column:
    table: str
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
    select: list[Column] = field(default_factory=list)
    tables: list[str] = field(default_factory=list)
    where: list[tuple[str, Condition]] = field(default_factory=list)   
    group_by: list[Column] = field(default_factory=list)
    having: list[tuple[str, Condition]] = field(default_factory=list)
    order_by: list[tuple[Column, str]] = field(default_factory=list)   
    limit: int | None = None
