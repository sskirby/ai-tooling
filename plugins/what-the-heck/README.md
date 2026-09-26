# what-the-heck

Teach one idea at a time, prove it landed, then move on.

This file is the decision log: why each rule in the skill exists, what was
rejected, what it costs, and which eval pins it. Part 1 covers the teaching
format. Part 2 covers how this repo is built and verified.

> **Part 1 needs the author's pass.** The rules are the author's. The
> reconstruction of *why* is not. A decision log that confidently invents an
> author's reasoning is worse than none, because it launders a guess into an
> artifact others will cite. Correct anything below that is wrong.

## Evidence note

Measured on Opus 5.5.

Where each case stands, this run's `with` score / `without` score / delta:


| case                          | with | without | Δ     |
| ----------------------------- | ---- | ------- | ----- |
| opening                       | 1.00 | 0.25    | +0.75 |
| first-step                    | 0.88 | 0.25    | +0.63 |
| next-means-one-step           | 1.00 | 0.67    | +0.33 |
| closing                       | 1.00 | 0.87    | +0.13 |
| wrong-answer-reteaches        | 1.00 | 0.75    | +0.25 |
| shaky-reasoning-rechecks      | 1.00 | 0.83    | +0.17 |
| first-step-route-fits         | 1.00 | 0.83    | +0.17 |
| no-trigger-explain-and-do     | 1.00 | 1.00    | 0.00  |
| no-trigger-mid-implementation | 1.00 | 1.00    | 0.00  |
| no-trigger-task-ask           | 1.00 | 1.00    | 0.00  |


The mean delta is **+0.35 across the seven teaching cases**. The three `no-trigger-*` cases score a correct 0.00 by
design — the skill must not fire on those prompts and it does not — so
averaging them in drags the figure down for a reason that is a pass, not a
failure.

Of the scored graders across the seven teaching cases, 8 discriminate
cleanly, 6 discriminate only weakly (the baseline lands them 1 or 2 of 3:
`names-the-gotcha`, `recap-is-one-item-per-step`, `illustration-without-clutter`,
`advances-without-commentary`, `rechecks-before-moving-on`, `keeps-the-route`),
14 are inert (pass in both arms because bare Opus 5.5 already does the
behaviour), and 3 fail in the with arm (`check-requires-using-the-idea`,
`no-extraneous-prose` — see D4, D5 — and `step-one-is-new-to-them` — see
D11). Inert graders cluster mid-lesson: shaky 3/4, wrong-answer 3/4,
next-means 2/4. On Opus 5.5, the skill's measurable value is concentrated
in the opening and first step — not because the later behaviours don't
matter, but because the baseline already does most of them. See Open
("Graders that pass in both arms").

Run-to-run noise on a 3-run case is about ±0.20, so a delta smaller than
that on any single case is not signal.

---

## Part 1 — the teaching format

## D1 — The answer comes before the route

**Decision.** The short answer comes first, in one or two sentences; the
route and the steps that follow explain why it's true.

**Rejected.** Making the reader earn the answer by reading five steps
first.

**Cost.** A reader who only wanted the answer leaves after line one — the
right outcome, but read on turn count alone it looks like a lesson that
failed before it started.

**Pinned by.** evals/opening/ (answer-before-route).

## D2 — Route titles are claims

**Decision.** The route is a numbered list of 3–6 step titles, and each
title is a claim, not a topic: "The policy is AND-ed onto every scan," not
"Policy injection."

**Rejected.** Topic labels — faster to write, and they tell the reader
nothing about what they're about to learn.

**Cost.** Writing a route of claims costs real thought before any teaching
happens; a lazy route reverts to topic labels.

**Pinned by.** evals/opening/ (titles-are-claims, route-is-3-to-6-items).

## D3 — Exactly one calibration question

**Decision.** The opening asks exactly one calibration question, then
stops and waits for the reply before step 1.

**Rejected.** A short quiz up front; and, at the other extreme, guessing
the reader's level and skipping the question entirely.

**Cost.** One extra round trip before any teaching starts.

**Pinned by.** evals/opening/ (asks-about-the-reader, calibration-is-one-ask,
no-step-yet).

## D4 — Every step ends with a question you ask them

**Decision.** A step is not complete until the learner
answers a question that requires using the idea.

**Rejected.** Closing with "any questions?" — it asks the
learner to already know what they don't know, which is the
one thing they cannot do.

**Cost.** Roughly doubles the number of turns. Some users
find it slow; `next` is the escape hatch (see D7).

**Pinned by.** evals/first-step/ (check-requires-using-the-idea).

## D5 — Prose stays earned, not padded

**Decision.** Each step's prose stays tight and readable: no mannered
phrasing, no beating around the bush, no throat-clearing before the
point. A concept is never explained incompletely just to hit a count —
the author's ruling is that a step's length should be earned, not capped.

**Rejected.** A hard numeric word cap. Per the author, the cap's intent
was always tightness, not an arithmetic ceiling, and a long-but-earned
step should not have to break itself in two just to stay under a number.

**Cost.** Cutting narration without cutting content takes a real editing
pass — spotting a deletable sentence is harder than counting words.

**⚠ Skill and check disagree, deliberately.** `SKILL.md:60` still states
a 150-word hard budget; the check judges tightness instead. Until a
refinement pass reconciles them, this entry describes the author's ruling.

**Pinned by.** evals/first-step/ (no-extraneous-prose).

## D6 — Illustrate the step, without crowding it

**Decision.** Each step shows its idea rather than only asserting it — a
diagram, a worked example with concrete values, or an analogy. More than
one is fine where they help; what is not fine is illustration that crowds
the step.

**Rejected.** A strict one-picture-or-one-example rule, and at the other
extreme a step with nothing to look at.

**Cost.** "Crowding" is a judgement rather than a count, so this check
cannot be decided mechanically.

**⚠ Skill and check disagree, deliberately.** `SKILL.md:61` still reads
"**Exactly one picture or one worked example.** Not both, not three."
Until a refinement pass reconciles them, this entry describes the
author's ruling.

**Pinned by.** evals/first-step/ (illustration-without-clutter).

## D7 — `next` means one step, no commentary

**Decision.** `next` means one more step, delivered without commentary.

**Rejected.** Asking "are you sure you want to skip the check?" — it
punishes the reader for using the hatch that's supposed to be theirs to
use.

**Cost.** A reader can skip past a misunderstanding; that's their call to
make, not the skill's to prevent.

**Pinned by.** evals/first-step/ (escape-hatch-present);
evals/next-means-one-step/ (escape-hatch-present, exactly-one-step,
advances-without-commentary, step-three-not-a-dump).

## D8 — Never advance past a wrong answer

**Decision.** Never advance past a check the learner got wrong; re-teach
from a new angle. A right conclusion reached with shaky reasoning gets the
gap named and a re-check, not a pass.

**Rejected.** Repeating the step louder; accepting a right answer for the
wrong reason.

**Cost.** A confused reader spends longer on step 2 — which is the point:
the misunderstanding surfaces at step 2, not step 6.

**Pinned by.** evals/wrong-answer-reteaches/ (does-not-advance,
does-not-affirm-the-wrong-answer, issues-a-fresh-check,
reteaches-from-a-new-angle); evals/shaky-reasoning-rechecks/
(does-not-advance, does-not-simply-congratulate, names-the-specific-gap,
rechecks-before-moving-on).

## D9 — The close is the chain, then the one thing that bites

**Decision.** The close gives the whole chain back in about five lines,
one per step, then names the one thing most likely to bite them in
practice.

**Rejected.** A summary of topics covered — a table of contents after the
fact, not a chain.

**Cost.** Writing it well means having actually taught a chain rather than
a pile of facts.

**Pinned by.** evals/closing/ (names-the-gotcha, recap-is-one-item-per-step,
recap-is-easy-to-scan, causal-chain, no-further-check, no-new-step).

## D10 — Real names, real code

**Decision.** Diagrams use real names from the code — `orders`,
`company_rls`, `.claude/worktrees/` — never `foo`. ASCII pictures stay
under 72 columns and 12 lines. Worked examples cite the actual file and
line when the subject is in the repo.

**Rejected.** Generic placeholders — faster to write, and they teach
nothing about the reader's own system.

**Cost.** Requires reading the actual code before teaching it.

**Pinned by.** Unpinned. Grading this needs a fixture repo the judge can
check real names and line numbers against — see Open.

## D11 — Revise the route when the answer calls for it

**Decision.** After the calibration answer, if it shows the learner
already knows a step, or changes what's worth teaching, the route is
revised before step 1 and the revised route is shown. A route that
already fits stands as shown.

**Rejected.** Following the route already shown as if the answer changed
nothing — teaching a learner who writes SQL daily that a CTE is a named
subquery.

**Cost.** An extra beat before step 1 whenever the answer calls for a
revision — a second route shown after the first, on top of D3's
calibration round trip.

**Pinned by.** evals/first-step/ (step-one-is-new-to-them,
revised-route-is-shown); evals/first-step-route-fits/ (keeps-the-route,
route-not-repeated).

---

## Part 2 — build and verification

## B1 — One repo, one marketplace, one plugin

**Decision.** The repo is the marketplace and holds one plugin under
`plugins/`.

**Rejected.** A single-plugin repo with the manifest at the root.

**Cost.** One extra directory level today, for a shape that scales to a
second plugin without a restructure.

**Pinned by.** Unpinned by design; `claude plugin validate` and the lint
job check the shape on every push.

## B2 — Restated context, not resumed-session fixtures

**Decision.** Post-turn-1 behaviour in a case comes from inline restated
context in the prompt, not from a `context.history_file` pointing at a
sampled transcript. The restated context quotes what a grader needs to
compare against — the earlier route, the earlier explanation — not just a
summary of it.

**Rejected.** Resumed-session fixtures. The harness forces any case with
`context.history_file` into the `with` arm alone, which deletes the
ablation delta on exactly the cases that need it most. A sampled
transcript also runs to roughly 900 KB and carries account IDs, `cwd` and
`gitBranch`, all needing scrubbing on every regeneration.

**Cost.** The prompt describes the prior exchange instead of being it, so
a case can drift from what a real resumed session would contain, and it
can restate something false that no one but the model under test notices.
A one-off hand-check against a genuinely resumed session is planned and
has not been run, so this rests on the design argument above.

**Pinned by.** evals/first-step/, evals/first-step-route-fits/,
evals/closing/, evals/wrong-answer-reteaches/, evals/next-means-one-step/,
evals/shaky-reasoning-rechecks/.

## B3 — Hybrid case packaging

**Decision.** Cases with long rubrics use `prompt.md` + `graders/*.md`;
the two-grader negative-trigger cases use a single `case.yaml`.

**Rejected.** One format everywhere. Monolithic YAML buries 700-word
rubrics inline; splitting every two-grader case into its own directory of
files is ceremony for a case that small.

**Cost.** Two shapes to read, and to keep the linter honest about.

**Pinned by.** The lint job (`scripts/lint.rb`) validates both shapes on
every push; `ruby test/lint_test.rb` exercises the validator itself.

## B4 — No eval gate on PRs, just lint

**Decision.** No eval run on pull requests. A `workflow_dispatch`-only
workflow runs the suite by hand; a free lint check gates every PR instead.

**Rejected.** A required eval check on every PR. It costs real money per
run; GitHub withholds secrets from fork PRs so it would fail on every
outside contributor by construction; and dozens of LLM graders at roughly
95% reliability each go red on good PRs often enough to teach everyone to
ignore the check.

**Cost.** Regressions in behaviour are caught by a human running the suite
before merge, not automatically by CI.

**Pinned by.** The lint job; the pre-merge command documented in the root
README.

## B5 — The trigger excludes task requests

**Decision.** The skill's trigger is narrow: a request to perform a task
does not fire the skill, even when it carries an "I don't get this,
explain as you go" rider.

**Rejected.** Leaving the description broad and letting the skill fire on
"how do I add an index to this table?" — when it fired on a task request,
the lesson took over instead of the task getting done.

**Cost.** A genuine "explain this to me" phrased as a task request may now
go unanswered by the skill.

**Pinned by.** evals/no-trigger-task-ask/,
evals/no-trigger-mid-implementation/, evals/no-trigger-explain-and-do/
(the one that uses the description's own trigger vocabulary in a task
request).

## B6 — "Read the code first" ships unpinned

**Decision.** "When the subject is in this repo, read the code before
step 1" is deliberately unpinned in v1.

**Rejected.** Writing the case now. It needs a committed fixture repo plus
`context.add_dirs`, then a `tool_used` grader (`Read`, `min: 1`) and an
LLM grader for citing a real path and line number — a new class of asset
for one rule.

**Cost.** The rule can drift without the suite noticing.

**Pinned by.** Unpinned, by decision. See Open.

## B7 — Pin the model under test and the judge

**Decision.** The model under test is pinned to claude-opus-5-5 in every
case, and lint refuses a case with no pinned model. The judge is
claude-opus-5-5 too, passed as a full model ID in the root README's eval
command and in `eval.yml`.

**Rejected.** Leaving cases unpinned. An unpinned case runs on the CLI's
built-in default model — the eval sandbox never reads the user's
`settings.json` — which can change with a CLI update between two runs of
the same case, and no run records which model it hit. Omitting
`--judge-model` means Haiku.

**Cost.** The Opus judge costs more per run than a smaller one; the author
ruled the grader should be the more capable model. Judge and model under
test being the same model is a self-preference risk; both arms share it,
so it mostly cancels out of the delta but not out of either arm's absolute
score.

**Pinned by.** The lint rule that refuses an unpinned case;
`aggregate-result.json` records `model` on every pinned case.

## B8 — Load the skill by slash command in mid-lesson cases

**Decision.** The four mid-lesson cases — `next-means-one-step`,
`shaky-reasoning-rechecks`, `wrong-answer-reteaches`, `closing` — open
their prompt with `/what-the-heck:what-the-heck` instead of relying on a
natural-language trigger.

**Rejected.** Triggering these cases the same way as `opening` and
`first-step`. On claude-opus-5-5 no prompt wording fired the skill
reliably mid-lesson; the best reached about 1 in 3. In real use the skill
loads once, at turn 1, and stays loaded; a single-turn case can only
reproduce "already loaded" by loading it deterministically.

**Cost.** `skill-fired` (`tool_used: Skill`) cannot see a slash-loaded
skill, so those four cases don't carry it. The suite splits into cases
that test triggering (`opening`, `first-step`, `first-step-route-fits`,
the three `no-trigger-*` cases) and cases that test behaviour once loaded.
The without arm receives the command as plain text and says it isn't
installed; `advances-without-commentary` is told to ignore that line.

**Pinned by.** A canary check, reproducible and not committed: a throwaway
copy of the plugin whose `SKILL.md` body tells the model to end every
reply with a nonsense token, graded by regex. With the slash command the
token appears in every with-arm reply and no without-arm reply.

---

## Open


| Item                                                          | Open because                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Resolved by                                                                                                                      |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| A case for "read the code before step 1" (B6)                 | Needs a committed fixture repo and `context.add_dirs`; deliberately deferred                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | A later pass, if a run suggests the rule drifts                                                                                  |
| Closing-step brevity                                          | No grader checks the length of the "what will bite you" note                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | A refinement pass the author has accepted, and a grader for the note's length                                                    |
| Graders that pass in both arms                                | 14 of the 31 scored graders pass in both arms because bare Opus 5.5 already does the behaviour, so they add nothing to any delta: `opening/answer-before-route`; `next-means-one-step/exactly-one-step`, `step-three-not-a-dump`; `closing/causal-chain`, `recap-is-easy-to-scan`, `no-further-check`; `wrong-answer-reteaches/does-not-advance`, `does-not-affirm-the-wrong-answer`, `reteaches-from-a-new-angle`; `shaky-reasoning-rechecks/does-not-advance`, `does-not-simply-congratulate`, `names-the-specific-gap`; `first-step/revised-route-is-shown`; `first-step-route-fits/route-not-repeated` | A decision per grader. Marking them `arm: with-only` would lift the deltas by hiding that the baseline is good; they stay scored |
| `illustration-without-clutter`'s baseline verdict is unstable | It gives opposite verdicts on first-step baseline replies with the same illustration density: the rubric judges a single step, and the baseline teaches all five at once. The with arm is unaffected                                                                                                                                                                                                                                                                                                                                                                                                       | A stated rule for a multi-section baseline reply, or a baseline variant of the check                                             |
| `next-means-one-step`'s natural trigger rate                  | Without the description's old step-by-step clause, the case's prompt fires the skill naturally about 1 in 3 runs, down from 3 in 3                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | The author deciding whether to restore a short clause, weighed against the over-triggering B5 narrowed                           |
| The skill states a numeric word budget                        | `SKILL.md:60` says "≤150 words of prose. Hard budget"; the check grades tightness (D5)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | An author ruling: keep 150 as a real ceiling, or drop the number                                                                 |
| The skill says one illustration                               | `SKILL.md:61` says "Exactly one picture or one worked example"; the check allows several (D6)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | The refinement pass                                                                                                              |
| The B2 resumed-session hand-check                             | Planned as a one-off comparison against a genuinely resumed session; not yet performed                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Running it and recording the verdict in B2                                                                                       |
| Verifying the install on the published path                   | `origin/main` holds only `LICENSE`, so `/plugin marketplace add sskirby/ai-tooling` cannot resolve yet                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Merging the pull request, then adding the marketplace by its GitHub name and running one case against that install               |


