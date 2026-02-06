from __future__ import annotations
from dataclasses import dataclass

# Tipos de Portugol (para declarações)
TipoPortugol = str  # "inteiro" | "real" | "cadeia"


@dataclass(frozen=True)
class Expr:
    pass


@dataclass(frozen=True)
class NumInt(Expr):
    valor: int


@dataclass(frozen=True)
class NumReal(Expr):
    valor: float


@dataclass(frozen=True)
class StrLit(Expr):
    valor: str


@dataclass(frozen=True)
class VarRef(Expr):
    nome: str


@dataclass(frozen=True)
class BinOp(Expr):
    op: str  # '+', '-', '*', '/', etc.
    left: Expr
    right: Expr


@dataclass(frozen=True)
class Compare(Expr):
    op: str  # '>', '<', '>=', '<=', '==', '!='
    left: Expr
    right: Expr


@dataclass(frozen=True)
class Stmt:
    pass


@dataclass(frozen=True)
class If(Stmt):
    cond: Expr
    then_block: list[Stmt]
    else_block: list[Stmt] | None


@dataclass(frozen=True)
class While(Stmt):
    cond: Expr
    block: list[Stmt]


@dataclass(frozen=True)
class VarDecl(Stmt):
    tipo: TipoPortugol
    nome: str


@dataclass(frozen=True)
class Assign(Stmt):
    nome: str
    expr: Expr


@dataclass(frozen=True)
class Write(Stmt):
    expr: Expr


@dataclass(frozen=True)
class Program:
    comandos: list[Stmt]
