---
type: llm
focus: last_message
---

The learner said they ran into a `WITH` in a colleague's query and couldn't
follow it, and that they mostly write simple SELECTs. The route already shown
to them starts with "A CTE is a named subquery the rest of the statement can
refer to by name". For this learner that is the right place to start, so the
route needs no rewrite before step 1.

Judge the first step the reply teaches, or its first section if it teaches
several at once.

Pass if that first idea is the route's first item: what a CTE is — a
subquery named with `WITH` that the rest of the statement refers to by name.
Tying it to the colleague's query or to the learner's own SELECTs is fine.
Adjusting later route items is also fine when the reply says what in the
learner's answer calls for it.

Fail if the first idea taught skips past what a CTE is to how the planner
treats one (inlining, materialisation, filter pushdown), or if the reply
replaces or reorders the route with no reason drawn from the learner's answer.
