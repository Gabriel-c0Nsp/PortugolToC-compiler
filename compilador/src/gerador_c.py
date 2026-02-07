from __future__ import annotations

from .ast_nodes import (
    Program,
    Stmt,
    VarDecl,
    Assign,
    Write,
    If,
    While,
    ProcDecl,
    FuncDecl,
    CallStmt,
    Return,
    Param,
    Expr,
    NumInt,
    NumReal,
    StrLit,
    VarRef,
    BinOp,
    Compare,
    Call,
)
from .tabela_simbolos import TabelaDeSimbolos


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

        for stmt in program.comandos:
            if isinstance(stmt, (ProcDecl, FuncDecl)):
                self._rotina(stmt)
                self._emit("")

        self._emit("int main() {")
        self._indent += 1

        for stmt in program.comandos:
            if isinstance(stmt, (ProcDecl, FuncDecl)):
                continue
            self._stmt(stmt)

        self._emit("return 0;")
        self._indent -= 1
        self._emit("}")

        return "\n".join(self._out)

    def _emit(self, line: str) -> None:
        self._out.append(("  " * self._indent) + line)

    def _c_tipo(self, tipo: str) -> str:
        if tipo == "inteiro":
            return "int"
        if tipo == "real":
            return "float"
        if tipo == "cadeia":
            return "char*"
        raise ValueError(f"Tipo Portugol desconhecido: {tipo}")

    def _printf_fmt(self, tipo: str) -> str:
        if tipo == "inteiro":
            return "%d"
        if tipo == "real":
            return "%f"
        if tipo == "cadeia":
            return "%s"
        raise ValueError(f"Tipo não suportado em printf: {tipo}")

    def _params_c(self, params: list[Param]) -> str:
        if not params:
            return "void"

        parts: list[str] = []
        for p in params:
            if p.tipo == "cadeia":
                parts.append(f"char {p.nome}[100]")
            else:
                parts.append(f"{self._c_tipo(p.tipo)} {p.nome}")
        return ", ".join(parts)

    # rotinas (fora do main)
    def _rotina(self, stmt: Stmt) -> None:
        if isinstance(stmt, ProcDecl):
            self._proc_decl(stmt)
            return
        if isinstance(stmt, FuncDecl):
            self._func_decl(stmt)
            return
        raise ValueError(f"Rotina não suportada: {type(stmt).__name__}")

    def _proc_decl(self, stmt: ProcDecl) -> None:
        params = self._params_c(stmt.params)
        self._emit(f"void {stmt.nome}({params}) " + "{")
        self._indent += 1
        for s in stmt.body:
            self._stmt_rotina(s)
        self._indent -= 1
        self._emit("}")

    def _func_decl(self, stmt: FuncDecl) -> None:
        # semântica deve ter inferido retorno e colocado na tabela (global)
        sym = self.tabela.buscar(stmt.nome)
        if sym is None or getattr(sym, "kind", None) != "func" or getattr(sym, "retorno", None) is None:
            raise RuntimeError(f"Tipo de retorno da função '{stmt.nome}' não disponível para geração.")

        ret_tipo = sym.retorno
        if ret_tipo == "cadeia":
            raise RuntimeError("Função retornando 'cadeia' não suportada nesta versão.")

        params = self._params_c(stmt.params)
        self._emit(f"{self._c_tipo(ret_tipo)} {stmt.nome}({params}) " + "{")
        self._indent += 1
        for s in stmt.body:
            self._stmt_rotina(s)
        self._indent -= 1
        self._emit("}")

    # statements (main)
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
        if isinstance(stmt, CallStmt):
            self._call_stmt(stmt)
            return
        raise ValueError(f"Stmt não suportado: {type(stmt).__name__}")

    def _stmt_rotina(self, stmt: Stmt) -> None:
        if isinstance(stmt, Return):
            self._return(stmt)
            return
        self._stmt(stmt)

    def _var_decl(self, stmt: VarDecl) -> None:
        if stmt.tipo == "cadeia":
            self._emit(f"char {stmt.nome}[100];")
        else:
            self._emit(f"{self._c_tipo(stmt.tipo)} {stmt.nome};")

    def _assign(self, stmt: Assign) -> None:
        sym = self.tabela.buscar(stmt.nome)
        if sym is None or getattr(sym, "kind", None) != "var":
            raise RuntimeError(f"Variável '{stmt.nome}' não encontrada na geração de código.")

        tipo_var = sym.tipo

        tipo_expr = self.tipos_expr.get(id(stmt.expr))
        if tipo_expr is None:
            raise RuntimeError("Tipo da expressão não encontrado (semântica não preencheu tipos_expr).")

        rhs = self._expr(stmt.expr)

        if tipo_var == "cadeia":
            if tipo_expr != "cadeia":
                raise RuntimeError(
                    "Atribuição de cadeia com RHS não-cadeia não deveria passar da semântica."
                )
            self._emit(f"strcpy({stmt.nome}, {rhs});")
        else:
            self._emit(f"{stmt.nome} = {rhs};")

    def _write(self, stmt: Write) -> None:
        tipo = self.tipos_expr[id(stmt.expr)]
        fmt = self._printf_fmt(tipo)
        expr_c = self._expr(stmt.expr)
        self._emit(f'printf("{fmt}", {expr_c});')

    def _if(self, stmt: If) -> None:
        cond_c = self._expr(stmt.cond)
        self._emit(f"if ({cond_c}) " + "{")
        self._indent += 1
        for s in stmt.then_block:
            self._stmt_rotina(s)
        self._indent -= 1
        self._emit("}")

        if stmt.else_block is not None:
            self._emit("else {")
            self._indent += 1
            for s in stmt.else_block:
                self._stmt_rotina(s)
            self._indent -= 1
            self._emit("}")

    def _while(self, stmt: While) -> None:
        cond_c = self._expr(stmt.cond)
        self._emit(f"while ({cond_c}) " + "{")
        self._indent += 1
        for s in stmt.block:
            self._stmt_rotina(s)
        self._indent -= 1
        self._emit("}")

    def _call_stmt(self, stmt: CallStmt) -> None:
        call_c = self._expr(stmt.call)
        self._emit(f"{call_c};")

    def _return(self, stmt: Return) -> None:
        expr_c = self._expr(stmt.expr)
        self._emit(f"return {expr_c};")

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
        if isinstance(expr, Call):
            args = ", ".join(self._expr(a) for a in expr.args)
            return f"{expr.nome}({args})"
        if isinstance(expr, BinOp):
            return f"({self._expr(expr.left)} {expr.op} {self._expr(expr.right)})"
        if isinstance(expr, Compare):
            return f"({self._expr(expr.left)} {expr.op} {self._expr(expr.right)})"
        raise ValueError(f"Expr não suportada: {type(expr).__name__}")
