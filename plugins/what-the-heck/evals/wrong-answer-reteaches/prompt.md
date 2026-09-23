---
runs: 3
model: claude-opus-5-5
max_turns: 6
timeout_seconds: 300
allowed_tools: [Skill]
---

You're teaching me how the planner handles CTEs, in five steps. Here is step
2 of 5, exactly as you gave it to me:

> ## Step 2 of 5 — Postgres 12 stopped running the CTE first
>
> Before 12, a CTE was an optimization fence. The planner ran it on its own,
> stashed the rows, and only then let the rest of the statement touch them.
> Since 12 a plain CTE — not `MATERIALIZED`, not recursive, not
> side-effecting, referenced once — is inlined instead: the planner folds the
> CTE's body into the outer query and plans the whole statement as one unit.
>
> ```
>   PG 11                        PG 12+
>   ─────                        ──────
>   run the CTE → stash rows     one query tree
>   then run the outer query     one plan, decided together
> ```
>
> **Check:** given that, what happens to a filter written outside the CTE, on
> a column the CTE selects?

My answer: nothing, it can't reach inside. The CTE is a fence, so the filter
has to wait until the CTE has produced all its rows, and then it runs over the
result. That's why CTEs are slow.
