---
type: llm
focus: last_message
---

Earlier in the conversation the learner was shown this route:

1. A CTE is a named subquery the rest of the statement can refer to by name
2. Since Postgres 12 a plain CTE is normally inlined into the outer query
   rather than evaluated on its own first
3. Because it is inlined, a filter written outside the CTE can be pushed down
   into it and run earlier
4. MATERIALIZED, recursive and side-effecting CTEs are kept separate, and a
   filter cannot be pushed into those
5. A CTE referenced more than once is materialised by default: its body runs
   once and the result is shared, but no outer filter can be pushed into it

Pass if the reply teaches along that route unchanged. Also pass if it changes
the route and, before teaching anything, shows the new route as a list of
steps, so the learner can see where the lesson now goes.

Fail if the reply departs from the route — teaching first something that is
not route item 1, or dropping, merging or reordering items — without first
showing the revised route. Saying the plan has changed ("I'll skip points
2–5") without laying out the new steps does not count as showing it.
