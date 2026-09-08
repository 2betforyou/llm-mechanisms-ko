#!/usr/bin/env python3
"""Format LaTeX prose as one sentence per source line.

Only whitespace in prose is changed. Structural commands and protected
environments such as math, tables, figures, TikZ, and listings are preserved.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PROTECTED_ENVIRONMENTS = {
    "align",
    "align*",
    "aligned",
    "array",
    "bmatrix",
    "cases",
    "displaymath",
    "equation",
    "equation*",
    "figure",
    "figure*",
    "gather",
    "gather*",
    "longtable",
    "lstlisting",
    "minted",
    "multline",
    "multline*",
    "split",
    "table",
    "table*",
    "tabular",
    "tabularx",
    "tikzpicture",
    "verbatim",
}

STRUCTURAL_COMMAND = re.compile(
    r"^\s*\\(?:"
    r"addcontentsline|appendix|author|backmatter|bibliography|bibliographystyle|"
    r"bottomrule|caption|centering|chapter\*?|clearpairofpagestyles|date|"
    r"documentclass|endfirsthead|endhead|frontmatter|hypersetup|ihead|index|"
    r"input|label|listoffigures|listoftables|mainmatter|makeindex|maketitle|"
    r"midrule|Needspace|normalsize|ohead|part\*?|printindex|section\*?|setcounter|"
    r"small|subsection\*?|subsubsection\*?|tableofcontents|title|toprule"
    r")\b"
)
ITEM = re.compile(r"^(\s*\\item(?:\[[^]]*\])?\s*)(.*)$")
BEGIN = re.compile(r"\\begin\{([^}]+)\}")
END = re.compile(r"\\end\{([^}]+)\}")
ABBREVIATIONS = (
    "e.g.",
    "i.e.",
    "et al.",
    "Eq.",
    "Fig.",
    "Sec.",
    "No.",
    "vs.",
    "Dr.",
    "Mr.",
    "Mrs.",
)
CLOSERS = "'\"”’)]"


def has_unescaped_percent(line: str) -> bool:
    for index, char in enumerate(line):
        if char != "%":
            continue
        backslashes = 0
        cursor = index - 1
        while cursor >= 0 and line[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2 == 0:
            return True
    return False


def split_sentences(text: str) -> list[str]:
    sentences: list[str] = []
    start = 0
    brace_depth = 0
    in_math = False
    index = 0

    while index < len(text):
        char = text[index]
        escaped = index > 0 and text[index - 1] == "\\"
        if char == "$" and not escaped:
            in_math = not in_math
        elif not in_math and not escaped:
            if char == "{":
                brace_depth += 1
            elif char == "}" and brace_depth:
                brace_depth -= 1

        if char not in ".?!" or escaped or in_math or brace_depth:
            index += 1
            continue

        if char == "." and index > 0 and index + 1 < len(text):
            if text[index - 1].isdigit() and text[index + 1].isdigit():
                index += 1
                continue
        prefix = text[start : index + 1]
        if char == "." and prefix.endswith(ABBREVIATIONS):
            index += 1
            continue

        boundary = index + 1
        while boundary < len(text) and text[boundary] in CLOSERS:
            boundary += 1
        if boundary >= len(text) or not text[boundary].isspace():
            index += 1
            continue

        remainder = boundary
        while remainder < len(text) and text[remainder].isspace():
            remainder += 1
        if remainder < len(text):
            sentences.append(text[start:boundary].strip())
            start = remainder
            index = remainder
            continue
        index += 1

    tail = text[start:].strip()
    if tail:
        sentences.append(tail)
    return sentences


def format_text(source: str) -> str:
    lines = source.splitlines()
    output: list[str] = []
    environment_stack: list[str] = []
    chunk: list[str] = []
    chunk_indent = ""
    chunk_prefix = ""
    continuation_indent = ""

    def protected() -> bool:
        return any(name in PROTECTED_ENVIRONMENTS for name in environment_stack)

    def flush() -> None:
        nonlocal chunk, chunk_indent, chunk_prefix, continuation_indent
        if not chunk:
            return
        joined = " ".join(part.strip() for part in chunk)
        sentences = split_sentences(joined)
        for sentence_index, sentence in enumerate(sentences):
            if sentence_index == 0:
                output.append(f"{chunk_indent}{chunk_prefix}{sentence}")
            else:
                output.append(f"{continuation_indent}{sentence}")
        chunk = []
        chunk_indent = ""
        chunk_prefix = ""
        continuation_indent = ""

    def update_environment_stack(line: str) -> None:
        for name in BEGIN.findall(line):
            environment_stack.append(name)
        for name in END.findall(line):
            if name in environment_stack:
                reverse_index = environment_stack[::-1].index(name)
                del environment_stack[len(environment_stack) - reverse_index - 1]

    for line in lines:
        if protected():
            flush()
            output.append(line)
            update_environment_stack(line)
            continue

        if BEGIN.search(line) or END.search(line):
            flush()
            output.append(line)
            update_environment_stack(line)
            continue

        if not line.strip():
            flush()
            output.append(line)
            continue

        if line.lstrip().startswith("%") or has_unescaped_percent(line):
            flush()
            output.append(line)
            continue

        item_match = ITEM.match(line)
        if item_match:
            flush()
            prefix, body = item_match.groups()
            if not body:
                output.append(line)
                continue
            chunk = [body]
            chunk_prefix = prefix.lstrip()
            chunk_indent = prefix[: len(prefix) - len(prefix.lstrip())]
            continuation_indent = f"{chunk_indent}  "
            continue

        if STRUCTURAL_COMMAND.match(line) or line.lstrip().startswith(("\\[", "\\]")):
            flush()
            output.append(line)
            continue

        if not chunk:
            chunk_indent = line[: len(line) - len(line.lstrip())]
            continuation_indent = chunk_indent
        chunk.append(line)

    flush()
    result = "\n".join(output)
    if source.endswith("\n"):
        result += "\n"

    if "".join(source.split()) != "".join(result.split()):
        raise ValueError("formatter changed non-whitespace content")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("files", nargs="+", type=Path)
    args = parser.parse_args()

    changed: list[Path] = []
    for path in args.files:
        source = path.read_text(encoding="utf-8")
        formatted = format_text(source)
        if format_text(formatted) != formatted:
            raise ValueError(f"formatter is not idempotent for {path}")
        if formatted == source:
            continue
        changed.append(path)
        if args.write:
            path.write_text(formatted, encoding="utf-8")

    if args.check and changed:
        for path in changed:
            print(path)
        return 1
    if args.write:
        print(f"formatted {len(changed)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
