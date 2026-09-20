---
runs: 3
max_turns: 6
timeout_seconds: 300
allowed_tools: [Skill]
---

You're teaching me how the planner handles CTEs, in five steps. Step 2 of 5
was that a CTE in Postgres 12 and later is normally inlined into the outer
query. You asked me: given that, what happens to a filter written outside the
CTE, on a column the CTE selects?

My answer: it gets pushed down into the CTE, so it runs earlier. That's
because Postgres rewrites the whole query into one flat statement before
planning it, so by the time the planner sees it there's no CTE left at all —
it's just text substitution.
