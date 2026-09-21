# Projeto de Compiladores — Etapa 2: Gramática LL(1)

Este repositório é o ponto de partida da segunda etapa do compilador de
MicroC. O grupo completará as transformações e os conjuntos necessários para
converter a gramática fornecida em uma gramática LL(1).

Leia o [enunciado completo](ENUNCIADO.pdf) antes de começar. A especificação
da linguagem continua sendo a referência normativa; `MicroC.grammar` é o
artefato desta atividade e não deve ser alterado.

## Estrutura do repositório

```text
.
├── .github/workflows/tests.yml      # testes públicos no GitHub Actions
├── tests/test_grammar.py             # testes públicos
├── ENUNCIADO.pdf                    # enunciado da etapa
├── MicroC.grammar                   # gramática fornecida
├── grammar.py                       # algoritmos a implementar
├── runner.py                        # interface de linha de comando
├── pyproject.toml                   # configuração do pytest
└── requirements-dev.txt             # dependências dos testes
```

Implemente em `grammar.py`:

- remoção de recursão direta à esquerda;
- FIRST de uma sequência e de todos os não terminais;
- FOLLOW de todos os não terminais; e
- START de cada produção.

A leitura da gramática, a fatoração à esquerda, a procura por conflitos e o
runner já estão implementados. É permitido criar funções auxiliares, mas as
assinaturas e os atributos fornecidos não devem ser alterados.

## Preparação do ambiente

O ambiente de referência usa Python 3.12.

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

No Windows PowerShell, ative o ambiente com:

```powershell
.venv\Scripts\Activate.ps1
```

## Execução

Para transformar a gramática, imprimir os conjuntos e verificar LL(1):

```sh
python runner.py MicroC.grammar
```

Para executar os testes públicos:

```sh
python -m pytest -q
```

O starter inicialmente falha com `NotImplementedError`. Os testes passam
progressivamente conforme cada algoritmo é implementado. Casos adicionais do
autograder verificarão outras gramáticas compatíveis com o contrato publicado.

## Antes de entregar

- não altere `MicroC.grammar` para eliminar os conflitos manualmente;
- confirme que FIRST e FOLLOW são calculados até um ponto fixo;
- confira que a produção vazia usa `ε`, mas internamente possui lado direito
  vazio;
- execute `python -m pytest -q`; e
- confira a aba **Actions** depois de cada `push`.
