"""Regression test for check_pr_command.py. Run: python3 test_guard.py"""
import json, pathlib, subprocess, sys, tempfile
chk = str(pathlib.Path(__file__).with_name("check_pr_command.py"))
sp = tempfile.mkdtemp()
GOOD = "**Impact:** x\n## Summary\n## Evidence\n## Merge Danger\n**Door:** two-way - y\n**Downstream:** none\n**Blast radius:** none\n"
pathlib.Path(sp, "pr-body.md").write_text(GOOD)
pathlib.Path(sp, "bad.md").write_text("just a body\n")
pathlib.Path(sp, "pii.md").write_text(GOOD + "ping someone@example.com\n")
C = "cre" + "ate"; P = "gh pr " + C
cases = [
  ("plain git", "git status", 0),
  ("good body file", f"{P} --title t --body-file {sp}/pr-body.md", 0),
  ("bad body file", f"{P} --body-file {sp}/bad.md", 2),
  ("pii body", f"{P} -F {sp}/pii.md", 2),
  ("--fill", f"{P} --fill", 2),
  ("after cd &&", f"cd /x && {P} --fill", 2),
  ("rtk wrapper", f"rtk {P} --fill", 2),
  ("abs path gh", f"/opt/homebrew/bin/{P} --fill", 2),
  ("gh -R flag", f"gh -R a/b pr {C} --fill", 2),
  ("env prefix", f"GH_HOST=x {P} --fill", 2),
  ("commit msg mention", f'git commit -m "blocks {P} when body is bad"', 0),
  ("echo mention", f'echo "{P} --fill"', 0),
  ("edit title only", "gh pr edit 3 --title n", 0),
  ("edit bad body", "gh pr edit 3 --body hi", 2),
]
bad = 0
for name, cmd, want in cases:
    r = subprocess.run([sys.executable, "-I", chk], input=json.dumps({"command": cmd}), text=True, capture_output=True)
    ok = r.returncode == want; bad += not ok
    print(("PASS" if ok else "FAIL"), name, r.returncode)
sys.exit(bad)
