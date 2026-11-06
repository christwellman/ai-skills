# pr-body guard

Blocks agent-created PRs whose body does not follow the `pr-body` template.

| File | Role |
|---|---|
| `check_pr_command.py` | All rules. Reads JSON on stdin. Exit 0 = allow, exit 2 = block. |
| `test_guard.py` | 14-case regression test. Run `python3 test_guard.py`. |
| `opencode-pr-body-guard.js` | OpenCode plugin. Calls the checker from `tool.execute.before`. |

## Rules

| Command | Result |
|---|---|
| `gh pr create` with `--fill`, `--web`, or no body | Blocked |
| `gh pr create` / `gh pr edit` with a body that misses a required part | Blocked |
| Body contains an email address (except `noreply@anthropic.com`) | Blocked |
| `gh pr edit` without `--body` / `--body-file` | Allowed |

Required parts: `**Impact:**`, `## Summary`, `## Evidence`, `## Merge Danger`, `**Door:** one-way|two-way`, `**Downstream:**`, `**Blast radius:**`.

## Install

Claude Code — add to `~/.claude/settings.json` under `hooks.PreToolUse`:

```json
{
  "matcher": "Bash",
  "hooks": [{ "type": "command", "command": "/usr/bin/env python3 -I <repo>/pr-body/guard/check_pr_command.py", "timeout": 5 }]
}
```

OpenCode:

```bash
ln -s <repo>/pr-body/guard/opencode-pr-body-guard.js ~/.config/opencode/plugins/pr-body-guard.js
```

## Limits

- It checks shape, not quality. A body with empty sections passes.
- It matches `gh` only in command position (start, or after `;`, `&&`, `|`, `(`, a newline, or `$(`), with `rtk`, `env`, or a path prefix allowed. Mentions in commit messages or `echo` pass.
- PRs opened in the browser or with `gh api` are not checked.
- To turn it off, remove the hook entry or the plugin symlink.
