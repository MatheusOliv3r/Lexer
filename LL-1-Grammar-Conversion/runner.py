from __future__ import annotations

import sys
from pathlib import Path

from grammar import Grammar


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("uso: python runner.py arquivo.grammar", file=sys.stderr)
        return 2

    try:
        grammar = Grammar.from_file(Path(args[0]))
        grammar.eliminate_all_direct_left_recursion()
        grammar.left_factor()
        grammar.build_sets()
    except (OSError, UnicodeError, ValueError, RuntimeError) as error:
        print(f"erro: {error}", file=sys.stderr)
        return 2

    print(grammar)
    print()
    print(grammar.format_sets())
    print()

    conflicts = grammar.ll1_conflicts()
    if conflicts:
        print("A gramática ainda possui conflitos LL(1):")
        for first, second, overlap in conflicts:
            symbols = ", ".join(sorted(overlap))
            print(f"  {first}  <->  {second}: {{ {symbols} }}")
        return 1

    print("A gramática é LL(1).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
