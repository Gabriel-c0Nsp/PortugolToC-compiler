# PortugolToC-compiler
Projeto final da cadeira de Teoria da Computação e Computadores.

O projeto teve como objetivos principais:
- Implementar um `analisador léxico` usando expressões regulares.
- Construir um `analisador sintático` (descendente ou ascendente).
- Implementar `verificações semânticas básicas`.
- Criar e manipular uma `tabela de símbolos`.
- Gerar `código C` equivalente ao programa em Portugol.
- Integrar tudo em um `compilador funcional`.

## Como executar
Na raiz do projeto, você deve encontrar o script `run`, faça isso utilizando o comando `cd`, a partir do seu diretório. Exemplo:
```bash
cd PortugolToC-compiler
```

Dê permissão para o script de execução
```bash
chmod +x run
```

Agora basta executar o script `run`
```bash
./run
```

## Para executar manualmente (Windows)
Dentro da raiz do projeto, basta executar:
```bash
python ./compilador/main.py
```
