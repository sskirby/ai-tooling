---
runs: 3
model: claude-opus-5-5
max_turns: 6
timeout_seconds: 300
allowed_tools: [Skill]
---

Earlier in this conversation I asked you "what the heck is a CTE?". You've
been teaching me how the planner handles them, in five steps:

1. A CTE is a named subquery the rest of the statement can refer to by name.
2. Since Postgres 12 a plain CTE is normally inlined into the outer query
   rather than evaluated on its own first.
3. Because it is inlined, a filter written outside the CTE can be pushed
   down into it and run earlier.
4. MATERIALIZED, recursive and side-effecting CTEs are kept separate, and a
   filter cannot be pushed into those.
5. A CTE referenced twice can be evaluated twice.

For step 5 you asked me what that means for a CTE wrapping an expensive
aggregate that two later branches both read. I said the aggregate could run
twice, so I'd materialise it or push it into a temp table if the plan shows
the double scan.

That was the last step. Can you give me the closing recap?
