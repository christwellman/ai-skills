#!/usr/bin/env python3
"""Block `gh pr create` / `gh pr edit --body` unless the body follows the pr-body skill template.

Shared by the Claude Code PreToolUse hook and the OpenCode plugin.
Reads JSON on stdin: Claude Code hook input ({"tool_input": {"command"}, "cwd"})
or the plain shape ({"command", "cwd"}). Exit 0 = allow, exit 2 = block (reason on stderr).
"""
import json
import os
import re
import sys

# Match only when gh is in command position (start, or after ; & | ( newline $( ),
# optionally behind rtk/command/env wrappers. Mentions inside commit messages or echo do not match.
PR_CMD = re.compile(
    r"(?:^|[;&|(\n]|\$\()\s*(?:(?:rtk|command|exec|env)\s+|\w+=\S*\s+)*"
    r"(?:\S*/)?gh\s+(?:--?\S+\s+\S+\s+)*pr\s+(create|new|edit)\b"
)
BODY_FILE = re.compile(r"(?:--body-file|-F)(?:=|\s+)(['\"]?)([^\s'\"]+)\1")
BODY_INLINE = re.compile(r"(?:--body|-b)(?:=|\s)")
CAT_SUBST = re.compile(r"\$\(\s*cat\s+(['\"]?)([^\s'\")]+)\1\s*\)")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
EMAIL_ALLOW = {"noreply@anthropic.com"}

REQUIRED = [
    (r"\*\*Impact:\*\*", "**Impact:** line"),
    (r"^##\s+Summary\b", "## Summary"),
    (r"^##\s+Evidence\b", "## Evidence"),
    (r"^##\s+Merge Danger\b", "## Merge Danger"),
    (r"\*\*Door:\*\*\s*(one-way|two-way)", "**Door:** one-way|two-way"),
    (r"\*\*Downstream:\*\*", "**Downstream:** line"),
    (r"\*\*Blast radius:\*\*", "**Blast radius:** line"),
]

HOW_TO_FIX = (
    "Load the pr-body skill (Claude Code: Skill tool `pr-body`; OpenCode: skill `pr-body`), "
    "draft the body with its template, show it to the user, write it to a file, "
    "and pass it with --body-file <file>."
)


def block(reason: str) -> None:
    sys.stderr.write(f"Blocked by pr-body guard: {reason}\n{HOW_TO_FIX}\n")
    sys.exit(2)


def read_file(path: str, cwd: str) -> str | None:
    path = os.path.expanduser(path)
    if not os.path.isabs(path):
        path = os.path.join(cwd, path)
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)
    command = (data.get("tool_input") or {}).get("command") or data.get("command") or ""
    cwd = data.get("cwd") or os.getcwd()

    match = PR_CMD.search(command)
    if not match:
        sys.exit(0)
    is_edit = match.group(1) == "edit"
    file_match = BODY_FILE.search(command)
    has_inline = bool(BODY_INLINE.search(command))

    if is_edit and not (file_match or has_inline):
        sys.exit(0)  # title/label/reviewer edits do not touch the body

    if file_match and file_match.group(2) != "-":
        body = read_file(file_match.group(2), cwd)
        if body is None:
            block(f"cannot read body file {file_match.group(2)!r}.")
    elif has_inline or (file_match and file_match.group(2) == "-"):
        cat = CAT_SUBST.search(command)
        body = (read_file(cat.group(2), cwd) if cat else None) or command
    else:
        block("no PR body given (--fill, --web, or a missing --body is not allowed).")

    missing = [label for pattern, label in REQUIRED if not re.search(pattern, body, re.I | re.M)]
    if missing:
        block("PR body is missing pr-body template parts: " + ", ".join(missing) + ".")

    emails = {e for e in EMAIL.findall(body) if e.lower() not in EMAIL_ALLOW}
    if emails:
        block("PR body contains email addresses. Evidence must be aggregates only, with no PII.")

    sys.exit(0)


if __name__ == "__main__":
    main()
