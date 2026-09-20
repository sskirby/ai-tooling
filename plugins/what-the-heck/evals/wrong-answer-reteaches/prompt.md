---
runs: 3
max_turns: 6
timeout_seconds: 300
allowed_tools: [Skill]
---

You're teaching me how the planner handles CTEs, in five steps. Step 2 of 5
was that a CTE in Postgres 12 and later is normally inlined into the outer
query rather than evaluated on its own first. You asked me: given that, what
happens to a filter written outside the CTE, on a column the CTE selects?

My answer: nothing, it can't reach inside. The CTE is a fence, so the filter
has to wait until the CTE has produced all its rows, and then it runs over the
result. That's why CTEs are slow.
