import sys
import os
import argparse
import pprint
import json


def cmd_parse(args):
    from .phplex import lexer as base_lexer
    from .phpparse import make_parser

    parser = make_parser(args.debug)

    if args.file == "-":
        source = sys.stdin.read()
        filename = "<stdin>"
    else:
        with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
        filename = args.file

    lexer = base_lexer.clone()
    lexer.lineno = 1

    try:
        result = parser.parse(source, lexer=lexer)
    except SyntaxError as e:
        print(f"{filename}: {e}", file=sys.stderr)
        sys.exit(1)

    if result is None:
        result = []

    if args.output:
        with open(args.output, "w") as f:
            for item in result:
                if hasattr(item, "generic"):
                    item = item.generic()
                pprint.pprint(item, stream=f)
        print(f"AST dumped to {args.output} ({len(result)} nodes)")
    else:
        for item in result:
            if hasattr(item, "generic"):
                item = item.generic()
            pprint.pprint(item)

    parser.restart()


def cmd_lex(args):
    from .phplex import full_lexer

    if args.file == "-":
        source = sys.stdin.read()
    else:
        with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()

    lexer = full_lexer.clone()
    lexer.input(source)

    while True:
        tok = lexer.token()
        if not tok:
            break
        if args.skip_whitespace and tok.type == "WHITESPACE":
            continue
        print(f"{tok.type:30s} {tok.value!r:40s} line {tok.lineno}")


def cmd_check(args):
    from .phplex import lexer as base_lexer
    from .phpparse import make_parser

    parser = make_parser(False)
    success = 0
    failed = 0
    errors = []

    for root, _, files in os.walk(args.directory):
        for f in files:
            if not f.endswith(".php"):
                continue
            filepath = os.path.join(root, f)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as fh:
                    code = fh.read()
                lexer = base_lexer.clone()
                lexer.lineno = 1
                parser.parse(code, lexer=lexer)
                success += 1
            except Exception as e:
                failed += 1
                if args.verbose and len(errors) < 20:
                    rel = os.path.relpath(filepath, args.directory)
                    errors.append(f"  {rel}: {e}")
            finally:
                parser.restart()

    total = success + failed
    pct = (success / total * 100) if total else 0
    print(
        f"{os.path.basename(args.directory)}: "
        f"{success}/{total} ({pct:.1f}%) parsed, {failed} failed"
    )
    for err in errors:
        print(err)


def _node_to_dict(node):
    if node is None:
        return None
    if isinstance(node, (bool, int, float, str)):
        return node
    if isinstance(node, list):
        return [_node_to_dict(n) for n in node]
    if not hasattr(node, "fields"):
        return repr(node)
    d = {"_type": node.__class__.__name__}
    for field in node.fields:
        d[field] = _node_to_dict(getattr(node, field))
    if node.lineno is not None:
        d["lineno"] = node.lineno
    return d


def _parse_source(parser, base_lexer, source):
    lexer = base_lexer.clone()
    lexer.lineno = 1
    result = parser.parse(source, lexer=lexer)
    parser.restart()
    return result or []


def _parse_one_file(parser, base_lexer, filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read()
    return _parse_source(parser, base_lexer, source)


def cmd_ast_json(args):
    from .phplex import lexer as base_lexer
    from .phpparse import make_parser

    parser = make_parser(False)
    path = args.file

    if os.path.isdir(path):
        all_data = {}
        success = 0
        failed = 0
        for root, _, files in os.walk(path):
            for fname in files:
                if not fname.endswith(".php"):
                    continue
                filepath = os.path.join(root, fname)
                rel = os.path.relpath(filepath, path)
                try:
                    result = _parse_one_file(parser, base_lexer, filepath)
                    all_data[rel] = [_node_to_dict(n) for n in result]
                    success += 1
                except Exception as e:
                    all_data[rel] = {"error": str(e)}
                    failed += 1

        output = json.dumps(all_data, indent=2, default=repr)
        total = success + failed
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"JSON AST dumped to {args.output} ({total} files, {failed} errors)")
        else:
            print(output)
        return

    if path == "-":
        source = sys.stdin.read()
        try:
            result = _parse_source(parser, base_lexer, source)
        except SyntaxError as e:
            print(f"<stdin>: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            result = _parse_one_file(parser, base_lexer, path)
        except SyntaxError as e:
            print(f"{path}: {e}", file=sys.stderr)
            sys.exit(1)

    data = [_node_to_dict(n) for n in result]
    output = json.dumps(data, indent=2, default=repr)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"JSON AST dumped to {args.output} ({len(result)} nodes)")
    else:
        print(output)


def cmd_version(args):
    print("phply8 1.3.0")
    print("PHP 8.0-8.4 parser built on PLY (LALR)")


def main():
    p = argparse.ArgumentParser(
        prog="phply",
        description=(
            "PHP 8.x lexer and parser for Python\n"
            "PEP8 IS IMPORTANT, COMPLY !!!\n"
            "\n"
            "Supports PHP 8.0 through 8.4 syntax including enums,\n"
            "match expressions, named arguments, and more."
        ),
        epilog=(
            "examples:\n"
            "  phply parse index.php              Parse a file and print AST\n"
            "  phply parse index.php -o ast.txt   Save AST to file\n"
            "  phply lex index.php -s             Tokenize, skip whitespace\n"
            "  phply check src/                   Check parse rate on a directory\n"
            "  phply check src/ -v                Show which files fail\n"
            "  phply json index.php               Dump AST as JSON\n"
            "  phply json src/ -o ast.json        Dump entire directory to JSON\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--version", action="store_true", help="Show version info")
    sub = p.add_subparsers(dest="command")

    sp = sub.add_parser(
        "parse",
        help="Parse a PHP file and print its AST",
        description="Parse a PHP file into an abstract syntax tree and display it.",
    )
    sp.add_argument("file", help="PHP file (use - for stdin)")
    sp.add_argument("-o", "--output", help="Write AST output to a file")
    sp.add_argument(
        "-d", "--debug", action="store_true", help="Show parser debug trace"
    )

    sp = sub.add_parser(
        "lex",
        help="Tokenize a PHP file",
        description="Run the lexer on a PHP file and print each token.",
    )
    sp.add_argument("file", help="PHP file (use - for stdin)")
    sp.add_argument(
        "-s", "--skip-whitespace", action="store_true", help="Hide whitespace tokens"
    )

    sp = sub.add_parser(
        "check",
        help="Test parse rate on a directory of PHP files",
        description=(
            "Walk a directory, parse every .php file, "
            "and report success/failure counts."
        ),
    )
    sp.add_argument("directory", help="Directory to scan for .php files")
    sp.add_argument(
        "-v", "--verbose", action="store_true", help="List individual failures"
    )

    sp = sub.add_parser(
        "json",
        help="Dump AST as JSON (file or directory)",
        description="Parse a PHP file or directory and output the AST in JSON format.",
    )
    sp.add_argument("file", help="PHP file or directory")
    sp.add_argument("-o", "--output", help="Write JSON to a file instead of stdout")

    args = p.parse_args()

    if args.version:
        cmd_version(args)
        return

    commands = {
        "parse": cmd_parse,
        "lex": cmd_lex,
        "check": cmd_check,
        "json": cmd_ast_json,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
