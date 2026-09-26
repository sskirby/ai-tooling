---
type: llm
focus: last_message
---

Judge the reply's prose: everything except fenced code blocks, ASCII
diagrams, the closing check question and its escape-hatch line.

Every sentence does work. It carries part of the idea, states an assumption
the reader needs to know about, or asks for something the next step depends
on. The test for each sentence: could it be deleted with nothing lost?

Fail if the prose carries sentences that could go:

- throat-clearing — praising the question, announcing what is about to be
  explained, or narrating the teaching instead of teaching;
- mannered or ornamental phrasing where a plain statement would say the
  same thing;
- beating around the bush — hedges, qualifications and caveats that do not
  change what the reader should believe;
- saying the same thing twice in different words;
- tangents the step's single idea does not need.

Do NOT fail for length. A long step whose every sentence earns its place
passes. An explanation cut short to look brief, leaving out a piece the idea
needs, is the failure to avoid, not the goal.
