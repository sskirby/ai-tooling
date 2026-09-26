---
type: llm
focus: last_message
---

The reply credits the learner's correct conclusion — the filter does get
pushed down — and names what is actually wrong with their mechanism:
inlining is a rewrite the planner performs on the query tree, not blind
text substitution of one piece of SQL into another.

Naming that gap is the whole test. Explaining it at length, drawing a
diagram, citing planner internals, or adding related detail such as the
cases where a CTE is kept separate are all fine and none of them count
against the reply.

Fail only if the reply says "not quite" without naming what is wrong, or if
it never credits the conclusion the learner got right.
