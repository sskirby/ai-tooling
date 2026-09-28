---
type: llm
focus: last_message
---

Judge ONLY the recap — the part that gives the lesson back step by step,
usually introduced by a lead-in such as "The chain, end to end". Ignore
everything around it.

The recap is a chain, not a pile. The steps appear in the order they were
taught, and each one follows from the one before it: the reason step 3 is
true is what step 2 established. It reads as something the learner could
repeat to a colleague and have it hold together.

Fail if the steps are out of order, or if the recap is a list of true
facts about the subject with no thread running between them.

Judge the causal thread only. Length, item count and formatting are
`recap-is-one-item-per-step` and `recap-is-easy-to-scan`'s business, not
this grader's — do not fail a sound chain for running long.
