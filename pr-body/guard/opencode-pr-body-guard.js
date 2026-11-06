// OpenCode plugin: block `gh pr create` unless the body follows the pr-body skill.
// All rules live in check_pr_command.py (shared with the Claude Code hook).
// Install: symlink this file into ~/.config/opencode/plugins/.
import { spawnSync } from "node:child_process"
import { realpathSync } from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

const CHECKER = join(dirname(realpathSync(fileURLToPath(import.meta.url))), "check_pr_command.py")

export const PrBodyGuard = async ({ directory }) => ({
  "tool.execute.before": async (input, output) => {
    if (input.tool !== "bash") return
    const command = output?.args?.command ?? ""
    if (!/\bgh\s+pr\s+(create|new|edit)\b/.test(command)) return
    const cwd = output?.args?.workdir || directory || process.cwd()
    const res = spawnSync("python3", ["-I", CHECKER], {
      input: JSON.stringify({ command, cwd }),
      encoding: "utf8",
    })
    if (res.status === 2) throw new Error(res.stderr.trim())
  },
})
