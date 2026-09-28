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

Where each case stands, with score / without score / delta. For a replay
case, `without` is its baseline twin (B9). The turn-1 rows,
`first-step-route-fits-replay` and the other replay rows come from three
separate runs of the current cases:


| case                            | with | without | Δ     |
| ------------------------------- | ---- | ------- | ----- |
| opening                         | 1.00 | 0.25    | +0.75 |
| first-step-replay               | 0.92 | 0.25    | +0.67 |
| closing-replay                  | 1.00 | 0.60    | +0.40 |
| wrong-answer-reteaches-replay   | 1.00 | 0.75    | +0.25 |
| shaky-reasoning-rechecks-replay | 0.92 | 0.67    | +0.25 |
| next-means-one-step-replay      | 1.00 | 1.00    | 0.00  |
| first-step-route-fits-replay    | 1.00 | 1.00    | 0.00  |
| no-trigger-explain-and-do       | 1.00 | 1.00    | 0.00  |
| no-trigger-mid-implementation   | 1.00 | 1.00    | 0.00  |
| no-trigger-task-ask             | 1.00 | 1.00    | 0.00  |


The mean delta is **+0.33 across the seven teaching cases**. The three `no-trigger-*` cases score a correct 0.00 by
design — the skill must not fire on those prompts and it does not — so
averaging them in drags the figure down for a reason that is a pass, not a
failure.

Of the 31 scored graders across the seven teaching cases, 11 discriminate
cleanly, 2 discriminate only weakly (the baseline lands them 1 or 2 of 3),
15 are inert (pass in both arms because bare Opus 5.5 already does the
behaviour, or the replay baseline copies it from its history), and 3 miss
in the with arm. Two are in first-step, where `check-requires-using-the-idea`
and `no-extraneous-prose` fail the same run of three. The third is
shaky-reasoning-rechecks' `rechecks-before-moving-on`, which fails one run
of three whose check asks how to find out whether a CTE was inlined rather
than testing the corrected reasoning. Inert graders cluster mid-lesson and
in first-step-route-fits: next-means 4/4, wrong-answer 3/4, shaky 2/4,
route-fits 2/2. See Open ("Graders that pass in both arms").

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

**Pinned by.** replays/first-step/ (check-requires-using-the-idea).

## D5 — Prose stays earned, not padded

**Decision.** Each step's prose stays tight and readable: no mannered
phrasing, no beating around the bush, no throat-clearing before the
point. A concept is never explained incompletely just to hit a count —
the author's ruling is that a step's length should be earned, not capped.

**Rejected.** A hard numeric word cap. Per the author, the point is
tightness, not an arithmetic ceiling, and a long-but-earned
step should not have to break itself in two just to stay under a number.

**Cost.** Cutting narration without cutting content takes a real editing
pass — spotting a deletable sentence is harder than counting words.

**⚠ Skill and check differ, deliberately.** `SKILL.md:60` keeps "≤150
words of prose. Hard budget." Replies run past it, but replacing it with a
tightness rule made first-step's prose and route decisions worse, so the
number stays as a steer. The check grades tightness, not the count.

**Pinned by.** replays/first-step/ (no-extraneous-prose).

## D6 — Illustrate the step, without crowding it

**Decision.** Each step shows its idea rather than only asserting it — a
diagram, a worked example with concrete values, or an analogy. More than
one is fine where they help; what is not fine is illustration that crowds
the step.

**Rejected.** A strict one-picture-or-one-example rule, and at the other
extreme a step with nothing to look at.

**Cost.** "Crowding" is a judgement rather than a count, so this check
cannot be decided mechanically.

**Pinned by.** replays/first-step/ (illustration-without-clutter).

## D7 — `next` means one step, no commentary

**Decision.** `next` means one more step, delivered without commentary.

**Rejected.** Asking "are you sure you want to skip the check?" — it
punishes the reader for using the hatch that's supposed to be theirs to
use.

**Cost.** A reader can skip past a misunderstanding; that's their call to
make, not the skill's to prevent.

**Pinned by.** replays/first-step/ (escape-hatch-present);
replays/next-means-one-step/ (escape-hatch-present, exactly-one-step,
advances-without-commentary, step-three-not-a-dump).

## D8 — Never advance past a wrong answer

**Decision.** Never advance past a check the learner got wrong; re-teach
from a new angle. A right conclusion reached with shaky reasoning gets the
gap named and a re-check, not a pass.

**Rejected.** Repeating the step louder; accepting a right answer for the
wrong reason.

**Cost.** A confused reader spends longer on step 2 — which is the point:
the misunderstanding surfaces at step 2, not step 6.

**Pinned by.** replays/wrong-answer-reteaches/ (does-not-advance,
does-not-affirm-the-wrong-answer, issues-a-fresh-check,
reteaches-from-a-new-angle); replays/shaky-reasoning-rechecks/
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

**Pinned by.** replays/closing/ (names-the-gotcha, recap-is-one-item-per-step,
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

**Pinned by.** replays/first-step/ (step-one-is-new-to-them,
revised-route-is-shown); replays/first-step-route-fits/ (keeps-the-route,
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

## B2 — Later turns come from a replayed transcript, not restated context

**Decision.** A case that tests a later turn resumes a transcript of the
earlier turns through `context.history_file`, generated from the current
`SKILL.md` on every run (B9). The earlier assistant turns are captured once
from a real run and edited to the canonical route.

**Rejected.** Restating the earlier turns inside one prompt. The model
reads a description of the exchange instead of having it, and the no-skill
arm has no conversation to act in: it replies that it cannot see the
earlier turns, or follows a route restated in its own prompt. Measured side
by side, that inflated `next-means-one-step`'s Δ to +0.42 and made
`first-step-route-fits`'s negative, −0.33; see
[docs/replay-evals.md](../../docs/replay-evals.md). Sampled real
transcripts: roughly 900 KB each, with account IDs, `cwd` and `gitBranch`
to scrub on every regeneration; a generated transcript carries none of it.

**Cost.** Earlier turns are fixed, edited text, where a real learner sees
whatever the model wrote at turn 1. The explainer lists the other
differences from real use.

**Pinned by.** replays/first-step/, replays/first-step-route-fits/,
replays/next-means-one-step/, replays/shaky-reasoning-rechecks/,
replays/wrong-answer-reteaches/, replays/closing/.

## B3 — Hybrid case packaging

**Decision.** Cases with long rubrics use `prompt.md` + `graders/*.md`;
the two-grader negative-trigger cases use a single `case.yaml`. Replay
sources in `replays/` use a third shape: `case.yaml` plus
`context.messages`, with `graders/*.md` beside it.

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

## B8 — The skill loads in the history, not by slash command

**Decision.** In a later-turn case the skill load is part of the replayed
history: a Skill tool call at turn 1 and the skill text it injects, as a
natural load leaves them in a real session. Nothing loads the skill during
the live turn.

**Rejected.** Opening the prompt with `/what-the-heck:what-the-heck`. The
whole prompt becomes the skill's `ARGUMENTS`, which on
`first-step-route-fits` dropped `keeps-the-route` from 19/20 to 11/20, and
the no-skill arm receives the command as text and says it isn't installed.
A natural-language trigger in the live turn: on claude-opus-5-5 no wording
fired the skill reliably mid-lesson; the best reached about 1 in 3.

**Cost.** A replay never calls Skill, so `skill-fired` (`tool_used: Skill`)
cannot apply to it, and the generator refuses that grader. Triggering is
tested only by the turn-1 cases: `opening` and the three `no-trigger-*`
cases.

**Pinned by.** evals/opening/ (skill-fired); replays/first-step/,
replays/first-step-route-fits/, replays/next-means-one-step/,
replays/shaky-reasoning-rechecks/, replays/wrong-answer-reteaches/,
replays/closing/.

## B9 — Replay later-turn cases with a paired baseline

**Decision.** Each replay case (B2) has a baseline twin with the same
turns, no skill load and only an empty stub plugin. `scripts/eval.py`
regenerates both transcripts from the current `SKILL.md`, runs the suite
once and pairs each case with its twin for Δ. Sources live in `replays/`;
[docs/replay-evals.md](../../docs/replay-evals.md) explains the mechanism.

**Rejected.** The CLI's with-without on a replay case: its without arm resumes
the same transcript, skill text included. Committing transcripts and linting
them against `SKILL.md`: regenerating on every run makes staleness impossible.

**Cost.** Earlier assistant turns carry no thinking blocks, and the baseline
sees earlier replies written in the skill's format, which inflates it and
shrinks Δ. The suite must be run through the wrapper.

**Pinned by.** replays/first-step/, replays/first-step-route-fits/,
replays/next-means-one-step/, replays/shaky-reasoning-rechecks/,
replays/wrong-answer-reteaches/, replays/closing/.

---

## Open


| Item                                                          | Open because                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Resolved by                                                                                                                      |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| A case for "read the code before step 1" (B6)                 | Needs a committed fixture repo and `context.add_dirs`; deliberately deferred                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | A later pass, if a run suggests the rule drifts                                                                                  |
| Graders that pass in both arms | 15 of the 31 scored graders pass in both arms, because bare Opus 5.5 already does the behaviour or the replay baseline copies it from the earlier turns in its history, so they add nothing to any delta: `opening/answer-before-route`; `first-step/step-one-is-new-to-them`; `first-step-route-fits/keeps-the-route`, `route-not-repeated`; `next-means-one-step/advances-without-commentary`, `escape-hatch-present`, `exactly-one-step`, `step-three-not-a-dump`; `shaky-reasoning-rechecks/does-not-simply-congratulate`, `names-the-specific-gap`; `wrong-answer-reteaches/does-not-affirm-the-wrong-answer`, `issues-a-fresh-check`, `reteaches-from-a-new-angle`; `closing/no-further-check`, `recap-is-easy-to-scan` | A decision per grader. Marking them `arm: with-only` would lift the deltas by hiding that the baseline is good; they stay scored |
| `illustration-without-clutter`'s baseline verdict is unstable | It gives opposite verdicts on first-step baseline replies with the same illustration density: the rubric judges a single step, and the baseline teaches all five at once. The with arm is unaffected                                                                                                                                                                                                                                                                                                                                                                                                       | A stated rule for a multi-section baseline reply, or a baseline variant of the check                                             |


