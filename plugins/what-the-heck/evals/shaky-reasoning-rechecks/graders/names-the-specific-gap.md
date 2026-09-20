---
type: llm
focus: last_message
---

The reply credits the correct conclusion — the filter is pushed down — and
then names the specific thing the learner has wrong: inlining is a planner
rewrite of the query tree with its own conditions, not blind text
substitution, and a CTE can still be kept separate (MATERIALIZED, or a
side-effecting or recursive CTE). Fail if it only says "not quite" without
naming what, and fail if it re-teaches the whole step rather than fixing just
this gap.
