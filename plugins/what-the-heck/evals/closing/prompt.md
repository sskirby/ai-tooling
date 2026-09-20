---
runs: 3
max_turns: 6
timeout_seconds: 300
allowed_tools: [Skill]
---

You've been teaching me how the planner handles CTEs, in five steps. We're
done: step 5 was that a CTE referenced twice can be evaluated twice, and you
asked me what that means for a CTE wrapping an expensive aggregate that two
later branches both read. I said the aggregate could run twice, so I'd
materialise it or push it into a temp table if the plan shows the double scan.

That was the last step.
