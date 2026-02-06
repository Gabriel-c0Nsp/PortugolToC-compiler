from dataclasses import dataclass


@dataclass
class Posicao:
    linha: int
    coluna: int


class ErroCompilador(Exception):
    def __init__(self, mensagem: str, pos: Posicao | None = None):
        self.mensagem = mensagem
        self.pos = pos

        if pos:
            super().__init__(f"[linha {pos.linha}, coluna {pos.coluna}] {mensagem}")
        else:
            super().__init__(mensagem)


class ErroLexico(ErroCompilador):
    pass


class ErroSintatico(ErroCompilador):
    pass
