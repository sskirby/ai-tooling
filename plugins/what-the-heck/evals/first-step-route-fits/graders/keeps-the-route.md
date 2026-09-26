---
type: llm
focus: last_message
---

The learner has been shown this route:

1. A CTE is a named subquery the rest of the statement can refer to by name
2. Since Postgres 12 a plain CTE is normally inlined into the outer query
   rather than evaluated on its own first
3. Because it is inlined, a filter written outside the CTE can be pushed down
   into it and run earlier
4. MATERIALIZED, recursive and side-effecting CTEs are kept separate, and a
   filter cannot be pushed into those
5. A CTE referenced more than once is materialised by default: its body runs
   once and the result is shared, but no outer filter can be pushed into it

They then said they are about to start using CTEs in reports, a colleague
warned them CTEs can make queries slow, and they have not written one yet.
Every item fits that learner, so the route should stand as shown.

Pass if the first step taught is route item 1 and the route is unchanged.

Fail if the reply drops, adds, merges or reorders any route item, whether it
says so in prose or shows a new list, or if the first step taught is anything
other than route item 1.
