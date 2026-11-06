---
name: pr-body
description: "Write a PR body for the current branch and open the PR with gh. Use when the user asks to open, write, draft, or describe a pull request, or says 'PR this'. Tuned for Airflow DAGs, Snowflake SQL, and Python ETL repos."
metadata:
  forked-from: "https://github.com/mattpocock/skills/tree/main/skills/engineering/pr"
  credits: "See CREDITS.md"
---

# pr-body

Write a PR body that a reviewer can check fast. Then open the PR on the user's yes.

## Workflow

| Step | Action |
|---|---|
| 1 | Read the repo's `CLAUDE.md` or `AGENTS.md`. Obey its PR rules (for example `Closes #N` lines, changelog wording, merge rules). Use its domain terms. If `GLOSSARY.md` exists, use its terms too. |
| 2 | Find the base branch. Read `git log <base>..HEAD` and `git diff <base>...HEAD`. |
| 3 | Find the host: run `git remote get-url origin`. If the host is not `github.com`, pass `--hostname <host>` to `gh` (for example a GitHub Enterprise host). |
| 4 | Find the task. If `HARBOR_ATTEMPT_ID` is set, or the branch, commits, or chat name an `H-xxxx` handle, add the Task line. Otherwise omit it. Do not ask. |
| 5 | Collect evidence (see Evidence). Run only read-only checks. Do not run a load or DDL to get evidence. |
| 6 | Draft the body with the template. Show the title and body to the user. |
| 7 | On the user's yes, push the branch if needed and run `gh pr create --title "<title>" --body-file <file>`. Give the user the PR URL. |

Never merge the PR. Never request reviewers unless the user names them.

A guard (`guard/check_pr_command.py`) blocks `gh pr create` and `gh pr edit --body` when the body misses the template's required parts or contains email addresses. `--fill` and `--web` are blocked. See `guard/README.md`.

## Template

```markdown
**Impact:** <one plain-English sentence: what changes for stakeholders or dashboard users>
**Task:** H-xxxx            <!-- only when a Harbor task exists -->

## Summary

<one or two sentences, then the smallest visual that makes the point>

## Evidence

| Check | Before | After |
|---|---|---|
| <check name> | <result> | <result> |

## Merge Danger

**Door:** <one-way | two-way> — <reason in one sentence>
**Downstream:** <tables, DAGs, dashboards that read what this PR changes, or "none">
**Blast radius:** <one word>

<optional: one or two sentences on what could break>

## Deploy                   <!-- only when deploy steps exist -->

| Item | Value |
|---|---|
| Environment | <dev VM | prod VM | both> |
| Airflow Variables / Connections | <new or changed names, never values> |
| Snowflake DDL / grants to run | <file paths> |
| Backfill | <no | yes: range and command> |

<repo-required lines, for example: Closes #N>
```

## Writing rules

Use ASD-STE100:

- Write short sentences. Put one idea in each sentence.
- Use active voice.
- Use tables, not paragraphs, when there are 3 or more items.
- Do not write a preamble, filler, or hedges.

## Summary

Pick the smallest view that makes the key point clear. Usually one view is enough. Never use more than two.

### DAG task graph

Show task dependencies. Use `diff` when the graph already exists.

```diff
 extract_orders
   >> stage_orders
+  >> capture_raw_snapshot
   >> merge_order_history
-  >> refresh_tableau_extract
+  >> refresh_tableau_extract  [trigger_rule=all_done]
```

### Table lineage

Show the flow from source to target. Name the schema.

```text
CRM export (xlsx)
  -> SALES_OPS.ORDERS_STAGE
       -> SALES_OPS.ORDER_HISTORY    (slim, unchanged)
       -> SALES_OPS.ORDER_SNAPSHOT_RAW (new, VARIANT)
            -> Tableau: Order Backlog
```

### Column diff

Show schema changes as a diff. Include type and nullability.

```diff
 ORDER_HISTORY
   ORDER_ID        VARCHAR   NOT NULL
   SNAPSHOT_DATE  DATE      NOT NULL
+  SOURCE_FILE    VARCHAR   NULL
-  LEGACY_FLAG    BOOLEAN
```

### SQL logic as pseudocode

Show the join, filter, and merge logic as steps. Do not paste the full SQL.

```text
for each staged row
  match history on ORDER_ID + SNAPSHOT_DATE
  if matched and row hash changed
    update
  if not matched
    insert
skip rows where ORDER_ID is null   # new
```

Put each visual next to the sentence it supports. Show only the tasks, tables, and columns the reviewer needs.

## Evidence

Show proof that the change works. Show a before and after.

| Rank | Evidence type | Examples |
|---|---|---|
| 1 | Snowflake before/after | Row counts, sums, null rates, distinct counts, reconciliation query results |
| 2 | Airflow run proof | DAG run ID, run state, task durations, a short log excerpt from the dev VM |
| 3 | Tests and dry runs | The test that failed before and passes now, `pytest` summary, DAG parse check, SQL compile or `EXPLAIN` |

If no evidence exists, write `Not verified:` and say what to run. Never claim a run you did not see.

### Data safety

Evidence goes into a PR that many people read. Obey these rules:

- Show aggregates only: counts, sums, rates, min/max dates.
- Do not show raw rows. Do not show names, emails, employee IDs, customer names, account IDs, or contract numbers.
- Show Airflow Variable and Connection names only. Never show values.
- Mask config values: `key=<redacted>`.
- Remove secrets and tokens from log excerpts.

## Merge Danger

### Door

A two-way door is cheap to roll back. A one-way door is not.

These changes are **one-way doors**:

- `DROP`, `TRUNCATE`, `DELETE` without a restorable source
- An overwrite or full-refresh load that replaces history
- DDL that drops or renames a column or table
- A change to a primary key or merge key
- A data change that already went to a stakeholder

If Time Travel or a clone gives a rollback path, say so in the reason. Do not change the door type because of it.

### Downstream

This line is required. List each table, view, DAG, and Tableau dashboard that reads the changed objects. Find them with `grep` in the repo and in any lineage doc (for example `docs/data-lineage.md`). If you cannot confirm the list, write `Not verified:` and name the objects you checked.

### Blast radius

Use one word. Examples: `none`, `table`, `DAG`, `dashboard`, `schema`, `org-wide`.

## Deploy

Add this section only when a deploy step exists. Name files and variable names. Never put production values in the PR body. Link the repo's runbook if one covers the procedure.
