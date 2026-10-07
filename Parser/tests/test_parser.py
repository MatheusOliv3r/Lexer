from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
CASES = Path(__file__).parent / "cases"

from Lexer import Lexer, TokenKind  # noqa: E402
from ast_nodes import (  # noqa: E402
    Assignment,
    BinaryExpr,
    BinaryOperator,
    Block,
    CallExpr,
    CallStmt,
    IntLiteral,
    SourceSpan,
    StringLiteral,
    TypeName,
    VarDecl,
    ast_to_dict,
)
from ast_printer import ast_to_dot, format_ast  # noqa: E402
from parser import Parser, ParserError  # noqa: E402


def parse(source: str):
    return Parser(Lexer(source).scan()).parse()


def parse_case(category: str, name: str):
    source = (CASES / category / name).read_text(encoding="utf-8")
    return parse(source)


def main_statements(name: str):
    program = parse_case("valid", name)
    main = next(function for function in program.functions if function.name == "main")
    return main.body.statements


def test_programa_vazio_e_funcao_com_parametros():
    assert parse_case("valid", "empty.mc").functions == []
    function = parse_case("valid", "functions.mc").functions[0]
    assert function.return_type is TypeName.BOOL
    assert function.name == "verificar"
    assert [(item.type, item.name) for item in function.parameters] == [
        (TypeName.INT, "x"),
        (TypeName.BOOL, "ativo"),
    ]


def test_declaracoes_atribuicoes_e_bloco_constroem_ast():
    result = main_statements("statements.mc")
    assert isinstance(result[0], VarDecl)
    assert result[0].initializer is None
    assert isinstance(result[2], Assignment)
    assert isinstance(result[3], Block)


def test_chamada_como_expressao_e_comando_constroi_ast():
    result = main_statements("calls.mc")
    assert isinstance(result[0].initializer, CallExpr)
    assert isinstance(result[1], CallStmt)
    assert result[2].value.arguments[0].name == "resultado"


def test_precedencia_e_associatividade_a_esquerda():
    expression = main_statements("expressions.mc")[0].value
    assert isinstance(expression, BinaryExpr)
    assert expression.operator is BinaryOperator.SUBTRACT
    assert expression.left.operator is BinaryOperator.SUBTRACT
    assert expression.left.right.operator is BinaryOperator.MULTIPLY


def test_controle_de_fluxo_e_bloco_aninhado():
    result = main_statements("control_flow.mc")
    assert result[0].else_block is not None
    assert len(result[1].body.statements[0].statements) == 1


def test_print_concatena_strings_adjacentes():
    statement = main_statements("print.mc")[0]
    assert isinstance(statement.items[0], StringLiteral)
    assert statement.items[0].value == "MicroC = "
    assert isinstance(statement.items[1], IntLiteral)


@pytest.mark.parametrize(
    "filename",
    [
        "empty_print.mc",
        "expression_statement.mc",
        "chained_assignment.mc",
        "string_expression.mc",
        "missing_braces.mc",
        "missing_semicolon.mc",
        "malformed_arguments.mc",
    ],
)
def test_programas_invalidos_sao_rejeitados(filename: str):
    with pytest.raises(ParserError) as caught:
        parse_case("invalid", filename)
    assert caught.value.line >= 1
    assert caught.value.column >= 1


def test_erro_sintatico_informa_token_e_posicao():
    with pytest.raises(ParserError) as caught:
        parse_case("invalid", "missing_semicolon.mc")
    assert caught.value.expected == {TokenKind.SEMICOLON}
    assert (caught.value.line, caught.value.column) == (3, 1)


def test_metadata_e_independente_e_nao_vai_para_json():
    span = SourceSpan(1, 1, 1, 2)
    first = IntLiteral(1, span=span)
    second = IntLiteral(1, span=span)
    first.metadata["tipo"] = object()
    assert second.metadata == {}
    assert first == second
    assert "metadata" not in ast_to_dict(first)


def test_visualizacao_em_arvore_expoe_campos_e_hierarquia():
    tree = format_ast(parse_case("valid", "functions.mc"))
    assert tree.startswith("Program\n├── functions[0]: FunctionDecl")
    assert "├── return_type: bool" in tree
    assert "├── parameters[0]: Parameter" in tree
    assert "│   ├── type: int" in tree
    assert "└── body: Block" in tree
    assert "span:" not in tree


def test_visualizacao_dot_expoe_nos_e_arestas():
    dot = ast_to_dot(parse_case("valid", "functions.mc"), show_spans=True)
    assert dot.startswith("digraph AST {")
    assert 'label="FunctionDecl\\nspan = ' in dot
    assert 'label="functions[0]"' in dot
    assert 'label="parameters[0]"' in dot
    assert dot.endswith("}")


def test_runner_imprime_json_da_ast():
    source = CASES / "valid" / "integrated.mc"
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "runner.py"), str(source)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stderr == ""
    tree = json.loads(result.stdout)
    assert tree["node"] == "Program"
    assert [function["name"] for function in tree["functions"]] == ["soma", "main"]
