from __future__ import annotations

from .ast_nodes import (
    Program, Stmt, VarDecl, Assign, Write, If, While,
    Expr, NumInt, NumReal, StrLit, VarRef, BinOp, Compare
)
from .tabela_simbolos import TabelaDeSimbolos
from .semantico import AnalisadorSemantico

class GeradorC:
    def __init__(self, tabela: TabelaDeSimbolos, tipos_expr: dict[int, str]) -> None:
        self.tabela = tabela
        self.tipos_expr = tipos_expr
        self._out: list[str] = []
        self._indent = 0

    def gerar(self, program: Program) -> str:
        self._out = []
        self._indent = 0

        # cabeçalho
        self._emit("#include <stdio.h>")
        self._emit("#include <string.h>")
        self._emit("")
        self._emit("int main() {")
        self._indent += 1

        for stmt in program.comandos:
            self._stmt(stmt)

        self._emit("return 0;")
        self._indent -= 1
        self._emit("}")

        return "\n".join(self._out)

    def _emit(self, line: str) -> None:
        self._out.append(("  " * self._indent) + line)

    def _c_tipo(self, tipo: str, nome: str | None = None) -> str:
        if tipo == "inteiro":
            return "int"
        if tipo == "real":
            return "float"
        if tipo == "cadeia":
            return "char"
        raise ValueError(f"Tipo Portugol desconhecido: {tipo}")

    def _printf_fmt(self, tipo: str) -> str:
        if tipo == "inteiro":
            return "%d"
        if tipo == "real":
            return "%f"
        if tipo == "cadeia":
            return "%s"
        raise ValueError(f"Tipo não suportado em printf: {tipo}")

    # Statements
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
        raise ValueError(f"Stmt não suportado: {type(stmt).__name__}")

    def _var_decl(self, stmt: VarDecl) -> None:
        if stmt.tipo == "cadeia":
            self._emit(f'char {stmt.nome}[100];')
        else:
            ctype = self._c_tipo(stmt.tipo)
            self._emit(f"{ctype} {stmt.nome};")

    def _assign(self, stmt: Assign) -> None:
        sym = self.tabela.buscar(stmt.nome)
        # semântica garante que existe
        assert sym is not None
        tipo_var = sym.tipo

        tipo_expr = self.tipos_expr.get(id(stmt.expr))
        # também garantido pela semântica
        assert tipo_expr is not None

        if tipo_var == "cadeia":
            if tipo_expr != "cadeia":
                raise ValueError("Atribuição de cadeia com RHS não-cadeia não deveria passar da semântica.")
            rhs = self._expr(stmt.expr)
            self._emit(f"strcpy({stmt.nome}, {rhs});")
        else:
            rhs = self._expr(stmt.expr)
            self._emit(f"{stmt.nome} = {rhs};")

    def _write(self, stmt: Write) -> None:
        tipo = self.tipos_expr[id(stmt.expr)]
        fmt = self._printf_fmt(tipo)
        expr_c = self._expr(stmt.expr)
        self._emit(f'printf("{fmt}", {expr_c});')

    def _if(self, stmt: If) -> None:
        cond_c = self._expr(stmt.cond)
        self._emit(f"if ({cond_c}) {{")
        self._indent += 1
        for s in stmt.then_block:
            self._stmt(s)
        self._indent -= 1
        self._emit("}")

        if stmt.else_block is not None:
            self._emit("else {")
            self._indent += 1
            for s in stmt.else_block:
                self._stmt(s)
            self._indent -= 1
            self._emit("}")

    def _while(self, stmt: While) -> None:
        cond_c = self._expr(stmt.cond)
        self._emit(f"while ({cond_c}) {{")
        self._indent += 1
        for s in stmt.block:
            self._stmt(s)
        self._indent -= 1
        self._emit("}")

    # Expressions
    def _expr(self, expr: Expr) -> str:
        if isinstance(expr, NumInt):
            return str(expr.valor)
        if isinstance(expr, NumReal):
            return str(expr.valor)
        if isinstance(expr, StrLit):
            return '"' + expr.valor.replace('"', '\\"') + '"'
        if isinstance(expr, VarRef):
            return expr.nome
        if isinstance(expr, BinOp):
            return f"({self._expr(expr.left)} {expr.op} {self._expr(expr.right)})"
        if isinstance(expr, Compare):
            return f"({self._expr(expr.left)} {expr.op} {self._expr(expr.right)})"
        raise ValueError(f"Expr não suportada: {type(expr).__name__}")
