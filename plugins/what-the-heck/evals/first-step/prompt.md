---
runs: 3
model: claude-opus-5-5
max_turns: 6
timeout_seconds: 300
allowed_tools: [Skill]
---

Earlier in this conversation I asked you "what the heck is a CTE?". This is
what you said:

> A CTE is a named subquery you write at the top of a statement with `WITH`,
> so the rest of the query can refer to it by name. It exists only for that
> one statement.
>
> Here's the route:
>
> 1. A CTE is a named subquery the rest of the statement can refer to by name
> 2. Since Postgres 12 a plain CTE is normally inlined into the outer query
>    rather than evaluated on its own first
> 3. Because it is inlined, a filter written outside the CTE can be pushed
>    down into it and run earlier
> 4. MATERIALIZED, recursive and side-effecting CTEs are kept separate, and a
>    filter cannot be pushed into those
> 5. A CTE referenced more than once is materialised by default: its body runs
>    once and the result is shared, but no outer filter can be pushed into it
>
> What prompted the question — did you run into a `WITH` in someone else's
> query, or are you trying to write one?

This is my reply to that:

I'm chasing a slow report query at work. It has three chained CTEs and the plan
looks nothing like I expected. I write SQL most days, but I've never thought
about what the planner does with a CTE.

Go ahead.
