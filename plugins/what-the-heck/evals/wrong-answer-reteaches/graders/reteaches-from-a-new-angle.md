---
type: llm
focus: last_message
---

The prompt quotes the teacher's original step 2 in full: its prose, and a
two-column PG 11 vs PG 12+ sketch whose content is abstract ("run the CTE →
stash rows" against "one query tree"). Judge the reply against that text,
which you can see.

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
