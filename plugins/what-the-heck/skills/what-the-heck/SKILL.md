---
name: what-the-heck
description: >
  Use when the user wants to genuinely understand something rather than
  just receive an answer — "what the heck is X", "explain X to me",
  "walk me through X", "I don't get X". Applies to concepts, tools, error
  messages, query plans and unfamiliar code. Not for a request to perform
  a task, even one carrying an "explain as you go" rider: do the task and
  explain in place instead.
---

# What The Heck

Teach one idea at a time, prove it landed, then move on.

A good explanation delivered as a lecture still fails. Correct prose, a nice diagram, and a closing
"any questions?" asks the learner to already know what they don't know — which is the one thing they
can't do. So every step ends with a question **you** ask **them**.

## The loop

```
  ┌─ opening ──────────────────────────────────────┐
  │  short answer + route + one calibration ask     │
  └───────────────────────┬─────────────────────────┘
                          ▼
          ┌──── step N ────────────────────┐
          │  claim → picture → check       │
          └───────────┬────────────────────┘
                      ▼
              they answer / ask
                      │
        ┌─────────────┴─────────────┐
        │ landed                    │ didn't
        ▼                           ▼
    next step              re-teach same idea,
                           different angle, re-check
```

## Opening message

Three parts, in this order, then stop:

1. **The short answer** — one or two sentences. They get the answer now; the steps explain *why* it's
   true. Never make them earn the answer by reading five steps.
2. **The route** — a numbered list of 3–6 step titles. Each title is a claim, not a topic:
   "The policy is AND-ed onto every scan", not "Policy injection".
3. **One calibration question: what prompted this?** Its answer tells you what is worth teaching,
   and usually how much they already know. An either/or can make it easier to answer ("did you run
   into this in someone else's code, or are you writing it yourself?"). Ask nothing else. If the
   question already says why they're asking, ask how much of X they already work with instead.
   Then wait for the reply before starting step 1.

## Each step

A step is four things and nothing else:

- **A heading**: `Step N of M — <the claim>`.
- **≤150 words of prose.** Hard budget. If the idea won't fit, it's two steps.
- **Exactly one picture or one worked example.** Not both, not three.
- **A check question.** One question, then stop and wait.

### Pictures

ASCII in a fenced block. Under 72 columns so it survives a terminal. Under 12 lines. Label the boxes
with the real names from the code — `orders`, `company_rls`, `.claude/worktrees/` — never `foo` or
`Component A`. Draw the *mechanism* (what moves, in what order, and where it goes wrong), not a
taxonomy of parts.

### Worked examples

Pick one concrete case and carry it through with real values. `company_id = 7` beats "a tenant id".
When the subject is in the repo, read the actual file and cite `path/to/file.rb:42` — a real example
they can go look at outdoes an invented one that's easier to write.

### Check questions

The check asks them to *use* the idea, not recite it. Something they can only answer if the model in
their head is right — a prediction, an odd case, or "which of these two would be slower, and why?".

Not this: "Does that make sense?" / "Any questions before I continue?"
This: "Given that, what happens to the plan when the query has no `company_id` in its WHERE clause?"

Close with the escape hatch on its own line: `(answer it, ask me anything, or say "next" to skip ahead)`.

## When they answer

| Their answer | Do this |
|---|---|
| Right, with the reasoning | Say what they got right in one line, go to the next step |
| Right conclusion, shaky reasoning | Name the gap, fix just that, re-check before moving on |
| Wrong | Don't repeat the step louder. Re-teach the same idea from a different angle — a new diagram, a smaller example, an analogy — then ask a fresh check |
| A question instead | Answer it at their depth, then return to the check |
| "next" / "skip" | Move on without comment. Their call |

Never advance past a check they got wrong. The whole point of the format is that the misunderstanding
gets caught at step 2 instead of surfacing at step 6.

## Closing

After the last step, give the whole chain back in about five lines — one line per step, in order, as
a causal chain they could repeat to someone else. Then name the one thing most likely to bite them in
practice.

## When the subject is in this repo

Read the code before step 1. Grounding in the real files is what separates this from a textbook: real
names, real values, real line numbers, and the actual surprising thing in *their* codebase rather than
the generic version of it. Do the reading up front so the steps flow without tool-call gaps.

## Common mistakes

- **Stacking two ideas into one step** because they're related. Related is exactly why they blur. Split.
- **Asking "make sense?"** — it only ever gets "yes".
- **Front-loading definitions.** Introduce a term the moment the picture needs it, not before.
- **Continuing after a vague answer** because they seemed roughly right. Re-check.
- **Dumping all steps at once** when they say "next". "Next" means one more step.
