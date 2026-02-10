# PortugolToC-compiler
Projeto final da cadeira de `Teoria da Computação e Computadores`.

Mini-transpilador em Python que traduz um subconjunto de Portugol para C,
cobrindo estruturas e tipos básicos, com suporte a inteiro, real, cadeia,
se/senao, enquanto, escreva, procedimentos e funções.

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
chmod +x ptc
```

Agora basta executar o script `run`
```bash
./ptc
```

## Para executar manualmente (Windows)
Dentro da raiz do projeto, basta executar:
```bash
python ./compilador/main.py
```

## Usando Google Colab
Utilizando a ferramenta `Google Colab` no seu navegador, você deverá importar o projeto através do arquivo zipado que se encontra na raiz do repositório, chamado `compilador.zip`.

Essa ação deve ocorrer no momento em que executar a célula de setup do projeto, ou utilizando a funcionalidade `Run all` do Colab. Um prompt será exibido solicitando que o usuário entre com o arquivo compilador.zip, já mencionado acima.

Vale ressaltar que a versão implementada através do Google Colab é a versão final referente ao curso de `Teoria da Computação e Compiladores`, e não deve ser atualizada após a data de envio do projeto. A versão CLI do projeto conta com mais funcionalidades e flexibilidade de execução, podendo ainda receber atualizações.
