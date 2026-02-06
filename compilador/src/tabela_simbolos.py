from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class SimboloVar:
    nome: str
    tipo: str  # "inteiro" | "real" | "cadeia"


class TabelaDeSimbolos:
    """
    Tabela com escopos em pilha:
    scopes[-1] é o escopo atual.
    """

    def __init__(self) -> None:
        self._scopes: list[dict[str, SimboloVar]] = [dict()]  # escopo global

    def push(self) -> None:
        self._scopes.append(dict())

    def pop(self) -> None:
        if len(self._scopes) == 1:
            raise RuntimeError("Não é permitido remover o escopo global.")
        self._scopes.pop()

    def declarar(self, nome: str, tipo: str) -> None:
        atual = self._scopes[-1]

        if nome in atual:
            raise ValueError(f"Identificador '{nome}' já declarado neste escopo.")
        atual[nome] = SimboloVar(nome=nome, tipo=tipo)

    def buscar(self, nome: str) -> SimboloVar | None:
        for scope in reversed(self._scopes):
            if nome in scope:
                return scope[nome]
        return None

    def escopo_nivel(self) -> int:
        return len(self._scopes) - 1
