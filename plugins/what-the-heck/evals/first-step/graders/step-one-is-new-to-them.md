---
type: llm
focus: last_message
---

The learner said they write SQL most days but have never thought about what
the planner does with a CTE. Judge the first step the reply teaches, or its
first section if it teaches several at once: is that idea something this
learner does not already know?

Pass if the first idea taught is about how the planner treats a CTE —
inlining, materialisation, optimisation fences, filter pushdown, or why the
plan does not follow the order the CTEs are written in. It does not matter
whether the reply revised the route to get there or went straight at it. A
one-line reminder of what a CTE is, used only to lead into that idea, is fine.

Fail if the first idea taught is what a CTE is: that it is a named subquery,
its `WITH` syntax, that chained CTEs read from the ones above them, or that
the names last for one statement. Framing it as a quick recap ("you already
know this part, so this step is short") still fails: the step spends the
learner's attention on what they said they know.
