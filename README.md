# phply

phply is a parser for the PHP programming language written using PLY, a
Lex/YACC-style parser generator toolkit for Python.

## Why?

Good question. Because I'm crazy. Because it seemed possible.

Things I'm interested in doing with it:

* Converting PHP code to Python
* Running PHP templates in a Python environment
* Learning more about parsing "industrial" languages, warts and all

## What does it stand for?

* phply -> PHP PLY
* phply -> PHP Hypertext Preprocessor Python Lex YACC
* phply -> PHP Hypertext Preprocessor Hypertext Preprocessor Python Lex Yet Another Compiler Compiler
* (... to be completed ...)

## How do you pronounce it?

If you're conservative, it's pronounced "pee aich ply". If you're liberal,
it's "fiply". And if you're anarchist, pronounce it however you want. Who am I
to tell you what to do?

## What's working?

* Lexer matching the standard PHP lexer token-for-token
* Parser and abstract syntax tree for most of the PHP grammar
* Script to convert PHP source to JSON-based ASTs
* Script to convert PHP source to Jinja2 source (experimental)

## What's not?

Some things can't be parsed yet. They are getting fewer by the day, but there
is still a fair amount of work to do:

* Labels and goto
* Some other stuff, probably

## Who's working on it?

See the [AUTHORS](https://github.com/viraptor/phply/blob/master/AUTHORS) file.

## Troubleshooting

### Couldn't create 'phply.parsetab'

Phply relies on `ply` to generate and cache some tables required for the parser.
These have been generated with the latest available version of ply for the phply
release. If you installed phply under a different user and a new `ply` was
released, the parsetab file cannot be automatically updated. Your options are
to:

* raise an issue for phply
* rebuild the package yourself

## How do I use it?

* Lexer test: python phply/phplex.py
* Parser test: python phply/phpparse.py
* JSON dump: cd tools; python php2json.py < input.php > output.json
* Jinja2 conversion: cd tools; python php2jinja.py < input.php > output.html
* Fork me on GitHub and start hacking :)

## Feature Matrix: PHP 8.2 AST

| Feature | PHP 5.6 Support | PHP 8.2 Support | Notes |
| :--- | :--- | :--- | :--- |
| **Primitives** (Int, Float, String, Bool) | ✅ | ✅ | Standard types supported. |
| **Arrays** (`array()`) | ✅ | ✅ | |
| **Short Arrays** (`[]`) | ✅ | ✅ | Added support for empty `[]` and populated short arrays. |
| **Type Hinting** (Scalars & Classes) | ✅ | ✅ | |
| **Nullable Types** (`?string`) | N/A | ✅ | Added via `type_hint` grammar. |
| **Union Types** (`int\|string`) | N/A | ✅ | Fully supported. |
| **Intersection Types** (`A&B`) | N/A | ✅ | Fully supported. |
| **DNF Types** (`(A&B)\|C`) | N/A | ✅ | Supported via recursive type rules. |
| **Math & Logic** (`+`, `-`, `&&`, etc.) | ✅ | ✅ | |
| **Exponentiation** (`**`, `**=`) | ✅ | ✅ | Added `POW` and `POW_EQUAL` lexer tokens. |
| **Ternary Operator** (`? :`) | ✅ | ✅ | |
| **Null Coalescing** (`??`) | N/A | ✅ | |
| **Null Coalescing Assignment** (`??=`) | N/A | ✅ | |
| **Nullsafe Operator** (`?->`) | N/A | ✅ | Emits new `NullsafeMethodCall` and `NullsafeObjectProperty` AST nodes. |
| **Match Expressions** (`match()`) | N/A | ✅ | Emits new `Match` and `MatchArm` AST nodes. |
| **`throw` as Expression** | N/A | ❌ | Currently only parses `throw` as a standalone statement. |
| **Variable Assignment** (`$a = 1`) | ✅ | ✅ | |
| **Array Destructuring** (`list()`) | ✅ | ✅ | |
| **Short Array Destructuring** (`[$a, $b] = []`) | N/A | ✅ | Added to `p_expr_list_assign`. |
| **Destructuring in `foreach`** (`foreach($arr as [$a])`) | N/A | ❌ | `foreach` grammar needs updating to support array assignment rules. |
| **Standard Declarations** | ✅ | ✅ | |
| **Return Types** (`: type`) | ✅ | ✅ | |
| **Variadic Arguments** (`...$args`) | ✅ | ✅ | Supported via `ELLIPSIS` token. |
| **Named Arguments** (`func(name: $val)`) | N/A | ✅ | |
| **Closures** (`function() use () {}`) | ✅ | ✅ | |
| **Static Closures** (`static function() {}`) | ✅ | ✅ | Added missing `STATIC` parsing logic. |
| **Arrow Functions** (`fn() => expr`) | N/A | ✅ | Emits `ArrowFunction` AST node. |
| **First-class Callables** (`strlen(...)`) | N/A | ✅ | Emits `Unpack` AST node inside function calls. |
| **Classes, Interfaces, Traits** | ✅ | ✅ | |
| **Anonymous Classes** (`new class {}`) | N/A | ✅ | Emits `AnonymousClass` AST node. |
| **Visibility Modifiers** (`public`, etc.) | ✅ | ✅ | |
| **Typed Properties** (`public int $x`) | N/A | ✅ | |
| **Readonly Properties** (`public readonly int $x`) | N/A | ✅ | |
| **Readonly Classes** (`readonly class X {}`) | N/A | ⚠️ | Parsing conflicts reverted to ensure standard class stability. Needs deeper AST integration. |
| **Constructor Property Promotion** | N/A | ✅ | Allows modifiers (e.g., `public`) inside function parameter definitions. |
| **Constant Modifiers** (`public const X = 1`) | N/A | ✅ | AST node updated to accept modifiers list. |
| **Dynamic Class Constants** (`User::{$name}`) | N/A | ❌ | Fails on curly braces in constant scopes. |
| **Enums** (`enum Status {}`) | N/A | ✅ | Fully supported with `Enum` and `EnumCase` AST nodes. |
| **Attributes** (`#[Route]`) | N/A | ⚠️ | Lexes and parses perfectly to prevent crashes. AST node is generated, but currently absorbed rather than strictly attached to the parent object to maintain backward compatibility. |
| **Goto Statements** (`goto label;`) | ✅ | ✅ | Supported via `Goto` and `Label` AST nodes. |
| **Non-capturing Catches** (`catch(Exception)`) | N/A | ❌ | Requires variable (`$e`) definition. |
