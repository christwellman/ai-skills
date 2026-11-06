# Credits

`pr-body` is a modified fork of the [`pr`](https://github.com/mattpocock/skills/tree/main/skills/engineering/pr) skill by [Matt Pocock](https://github.com/mattpocock), MIT licensed. The upstream license is in `LICENSE`.

The upstream Summary section's menu of visuals and its placement guidance came from [Dex Horthy](https://github.com/dexhorthy)'s [`show-me`](https://github.com/humanlayer/humanlayer) skill. This fork keeps that idea and replaces the UI examples with DAG, lineage, column, and SQL views.

## Changes from upstream

| Area | Change |
|---|---|
| Scope | Drafts the body, then opens the PR with `gh` on the user's yes |
| Host | Detects github.com or GitHub Enterprise from the remote |
| Header | Adds a plain-English Impact line and an optional Harbor Task line |
| Summary | DAG task graph, table lineage, column diff, SQL pseudocode |
| Evidence | Snowflake before/after, Airflow run proof, tests; aggregates only |
| Merge Danger | Required Downstream list; ETL one-way door rules |
| Deploy | New optional section |
| Style | ASD-STE100 |
