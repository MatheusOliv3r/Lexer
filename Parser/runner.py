from __future__ import annotations

import argparse
import json
from pathlib import Path

from Lexer import Lexer, LexerError
from ast_nodes import ast_to_dict
from ast_printer import ast_to_dot, format_ast
from parser import Parser, ParserError


def main(argv: list[str] | None = None) -> int:
    argument_parser = argparse.ArgumentParser(description="Execute o parser MicroC.")
    argument_parser.add_argument("source", type=Path, metavar="arquivo.mc")
    argument_parser.add_argument(
        "--format",
        choices=("json", "tree", "dot"),
        default="json",
        help="formato de saída da AST (padrão: json)",
    )
    argument_parser.add_argument(
        "--show-spans",
        action="store_true",
        help="inclua posições do código-fonte nas saídas tree e dot",
    )
    args = argument_parser.parse_args(argv)

    try:
        source = args.source.read_text(encoding="utf-8")
        program = Parser(Lexer(source).scan()).parse()
    except (OSError, UnicodeError) as error:
        argument_parser.error(f"erro ao ler {str(args.source)!r}: {error}")
        return 2
    except (LexerError, ParserError) as error:
        argument_parser.exit(1, f"{error}\n")
        return 1

    if args.format == "tree":
        print(format_ast(program, show_spans=args.show_spans))
    elif args.format == "dot":
        print(ast_to_dot(program, show_spans=args.show_spans))
    else:
        print(json.dumps(ast_to_dict(program), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
