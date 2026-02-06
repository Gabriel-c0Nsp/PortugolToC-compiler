from __future__ import annotations
from .ast_nodes import (
    Program,
    Stmt,
    VarDecl,
    Assign,
    Write,
    If,
    While,
    Expr,
    NumInt,
    NumReal,
    StrLit,
    VarRef,
    BinOp,
    Compare,
)

from .erros import ErroCompilador, ErroSemantico, Posicao
from .tabela_simbolos import TabelaDeSimbolos


class AnalisadorSemantico:
    def __init__(self) -> None:
        self.tabela = TabelaDeSimbolos()
        self.tipos_expr: dict[int, str] = {}

    def analisar(self, program: Program) -> None:
        for stmt in program.comandos:
            self._stmt(stmt)

    # -------------------------
    # Statements
    # -------------------------
    def _stmt(self, stmt: Stmt) -> None:
        if isinstance(stmt, VarDecl):
            self._var_decl(stmt)
            return

        if isinstance(stmt, Assign):
            self._assign(stmt)
            return

        if isinstance(stmt, Write):
            self._write(stmt)
            return

        if isinstance(stmt, If):
            self._if(stmt)
            return

        if isinstance(stmt, While):
            self._while(stmt)
            return

        raise ErroSemantico(f"Stmt não suportado: {type(stmt).__name__}")

    def _var_decl(self, stmt: VarDecl) -> None:
        try:
            self.tabela.declarar(stmt.nome, stmt.tipo)
        except ValueError as e:
            raise ErroSemantico(str(e))

    def _assign(self, stmt: Assign) -> None:
        sym = self.tabela.buscar(stmt.nome)

        if sym is None:
            raise ErroSemantico(f"Variável '{stmt.nome}' usada antes de declarar.")

        tipo_expr = self._expr(stmt.expr)
        tipo_var = sym.tipo

        if not self._atribuicao_compativel(tipo_var, tipo_expr):
            raise ErroSemantico(
                f"Atribuição incompatível: variável '{stmt.nome}' é {tipo_var}, expressão é {tipo_expr}."
            )

    def _write(self, stmt: Write) -> None:
        _ = self._expr(stmt.expr)

    def _if(self, stmt: If) -> None:
        tipo_cond = self._expr(stmt.cond)

        if tipo_cond != "bool":
            raise ErroSemantico(f"Condição do 'se' deve ser bool, mas é {tipo_cond}.")

        # escopo do then
        self.tabela.push()
        for s in stmt.then_block:
            self._stmt(s)
        self.tabela.pop()

        # escopo do else
        if stmt.else_block is not None:
            self.tabela.push()
            for s in stmt.else_block:
                self._stmt(s)
            self.tabela.pop()

    def _while(self, stmt: While) -> None:
        tipo_cond = self._expr(stmt.cond)

        if tipo_cond != "bool":
            raise ErroSemantico(
                f"Condição do 'enquanto' deve ser bool, mas é {tipo_cond}."
            )

        self.tabela.push()
        for s in stmt.block:
            self._stmt(s)
        self.tabela.pop()

    # -------------------------
    # Expressions
    # -------------------------
    def _expr(self, expr: Expr) -> str:
        if isinstance(expr, NumInt):
            return self._set_tipo(expr, "inteiro")

        if isinstance(expr, NumReal):
            return self._set_tipo(expr, "real")

        if isinstance(expr, StrLit):
            return self._set_tipo(expr, "cadeia")

        if isinstance(expr, VarRef):
            sym = self.tabela.buscar(expr.nome)
            if sym is None:
                raise ErroSemantico(f"Variável '{expr.nome}' usada antes de declarar.")
            return self._set_tipo(expr, sym.tipo)

        if isinstance(expr, BinOp):
            t1 = self._expr(expr.left)
            t2 = self._expr(expr.right)
            t = self._tipo_binop(expr.op, t1, t2)
            return self._set_tipo(expr, t)

        if isinstance(expr, Compare):
            t1 = self._expr(expr.left)
            t2 = self._expr(expr.right)
            self._tipo_compare(expr.op, t1, t2)
            return self._set_tipo(expr, "bool")

        raise ErroSemantico(f"Expr não suportada: {type(expr).__name__}")

    def _set_tipo(self, node: object, tipo: str) -> str:
        self.tipos_expr[id(node)] = tipo
        return tipo

    # -------------------------
    # Regras de tipos
    # -------------------------
    def _atribuicao_compativel(self, tipo_var: str, tipo_expr: str) -> bool:
        if tipo_var == tipo_expr:
            return True
        # promo: inteiro -> real
        if tipo_var == "real" and tipo_expr == "inteiro":
            return True

        return False

    # TODO: finalizar
    def _tipo_binop(self, op: str, t1: str, t2: str) -> str:
        if op in {"+", "-", "*", "/"}:
            if t1 == "cadeia" or t2 == "cadeia":
                raise ErroSemantico(f"Operação '{op}' não suportada para cadeia.")
            if t1 == "bool" or t2 == "bool":
                raise ErroSemantico(f"Operação '{op}' não suportada para bool.")

            if t1 == "real" or t2 == "real":
                return "real"
            return "inteiro"

        raise ErroSemantico(f"Operador binário desconhecido: {op}")

    # TODO: finalizar
    def _tipo_compare(self, op: str, t1: str, t2: str) -> None:
        if t1 == "cadeia" or t2 == "cadeia":
            raise ErroSemantico(f"Comparação '{op}' não suportada para cadeia.")
        if t1 == "bool" or t2 == "bool":
            raise ErroSemantico(f"Comparação '{op}' não suportada para bool.")
        # inteiro/real ok entre si
