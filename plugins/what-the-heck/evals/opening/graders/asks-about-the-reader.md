---
type: llm
focus: last_message
---

The reply ends by asking the reader about themselves or their situation — what
prompted the question, what they are working on, which database or codebase
they are in, how much of the subject they already use. Anything whose answer
would change how the lesson is pitched counts.

Two things do NOT count. A question about what the questioner MEANT — "if you
meant coefficient of thermal expansion rather than the SQL construct, let me
know" — disambiguates the topic; it does not calibrate the pitch. A closing
question that tests the reader's understanding of CTEs is a comprehension
check, not calibration.

Fail if the reply asks nothing about the reader, or if its only closing
question is one of those two kinds.
