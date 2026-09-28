---
type: llm
focus: last_message
---

The learner was taught this step 2 and answered its check wrongly:

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

Judge the reply against that quoted explanation.

The reply teaches the same idea again — that an inlined CTE lets the outer
filter be pushed down — and gives the learner something new to look at: a
concrete query, real plan output, numbers carried through, an analogy, or a
walk through what the planner does to a specific query. Any combination
qualifies.

Judge content, not layout. A reply may reuse the before/after or
side-by-side shape, and that is a pass when what fills it is new — plan nodes
instead of the abstract labels, a specific query and its effect instead of a
general statement. Bullets and diagrams are equally fine.

Fail only if the reply restates the quoted explanation's content with
nothing new added — the same abstract claims in different words, or the same
sketch with the same labels — or if it abandons the idea and teaches
something else instead.
