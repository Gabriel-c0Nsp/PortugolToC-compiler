import sys
from pprint import pprint

from src.lexer import Lexer
from src.parser import Parser
from src.semantico import AnalisadorSemantico
from src.gerador_c import GeradorC
from src.erros import ErroCompilador

if len(sys.argv) > 1:
    caminho = sys.argv[1]

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            codigo = f.read()
    except FileNotFoundError:
        print(f'Arquivo "{caminho}" não encontrado.\n')
        print('Tente "./ptc -h" para mais informações de uso.')
        sys.exit(1)
else:
    codigo = """
    inteiro x;
    x = 0;

    enquanto (x < 5) faca
      x = x + 1;
    fimenquanto

    escreva(x);
    """


print("\npara o código:\n")
print("=============================")
print(codigo)
print("=============================\n")

try:
    tokens = Lexer().tokenizar(codigo)
    arvore = Parser(tokens).parse()

    semantica = AnalisadorSemantico()
    semantica.analisar(arvore)

    gerador = GeradorC(semantica.tabela, semantica.tipos_expr)
    codigo_c = gerador.gerar(arvore)

    print("------- TOKENS -------")
    for token in tokens:
        print(token)

    print("\n------- AST -------")
    pprint(arvore)

    print("\n------- C -------")
    print(codigo_c)

except ErroCompilador as e:
    print(e)
