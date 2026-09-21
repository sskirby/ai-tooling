---
type: llm
focus: last_message
arm: with-only
---

The reply's calibration is a single ask.

One question may carry a clarifying rider that makes it easier to answer:
"what prompted this — did you hit a `WITH` block in someone else's query, or
are you untangling one of your own?" is ONE ask. The either/or narrows the same
question rather than adding a second, and it saves the reader guessing what
would be useful to say.

Fail if the reply raises a second, unrelated calibration topic — asking what
prompted the question AND which database they are on, or AND how comfortable
they are with subqueries. A second topic counts whether it arrives as its own
sentence or trails after in a parenthetical.

This grader is `with-only` on purpose: the baseline asks nothing about the
reader at all, so comparing the arms on it measures nothing. Its companion
`asks-about-the-reader` carries the arm comparison.
