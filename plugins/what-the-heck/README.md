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

Every entry below that cites an eval case is now backed by a single run,
`2026-09-25T05-03-33-276Z` — 3 runs/arm, 54 sessions, $10.92, CLI 2.1.282 —
with the model under test pinned to claude-opus-5-5 in every case and the
judge also claude-opus-5-5 (`--judge-model`, 3 votes). This is the only run
current entries pin to. Raw data:
`evals/results/2026-09-25T05-03-33-276Z/aggregate-result.json` (gitignored
— re-run the named case directory to reproduce a number instead of trusting
the file to still be there).

Every number from before this run graded a different model and a
different judge, and is history, not evidence. Cases were unpinned until
`218d252`, so they ran on the CLI's built-in default model — the eval
sandbox never reads the user's `settings.json` — and the CLI's `opus`
alias moved claude-opus-5 -> claude-opus-5-5 between 2.1.278 and 2.1.280,
somewhere in that window. So every earlier number is almost certainly
Opus 5, a strong inference rather than a verified one. The judge was
Haiku throughout that era, since no `--judge-model` flag was passed until
this run. See B9.

Where each case stands, this run's `with` score / `without` score / delta:

| case | with | without | Δ |
|---|---|---|---|
| opening | 1.00 | 0.25 | +0.75 |
| first-step | 0.89 | 0.06 | +0.83 |
| next-means-one-step | 1.00 | 0.75 | +0.25 |
| closing | 1.00 | 0.80 | +0.20 |
| wrong-answer-reteaches | 1.00 | 0.92 | +0.08 |
| shaky-reasoning-rechecks | 1.00 | 1.00 | 0.00 |
| no-trigger-explain-and-do | 1.00 | 1.00 | 0.00 |
| no-trigger-mid-implementation | 1.00 | 1.00 | 0.00 |
| no-trigger-task-ask | 1.00 | 1.00 | 0.00 |

The mean delta is **+0.35 across the six teaching cases** and **+0.24
across all nine**. Always say which population a mean covers: the three
`no-trigger-*` cases score a correct 0.00 by design — the skill must not
fire on those prompts and it does not — so averaging them in drags the
figure down for a reason that is a pass, not a failure.

An audit of this run (8 read-only Sonnet agents, every reply read) found
every grader verdict correct in all nine cases: no grader defects, judge
errors, prompt defects, or contamination. One finding survived an
adversarial refutation pass, and it is the open question already on record, now with stronger
evidence: `calibration-is-one-ask` is `FFF`, unanimous across all 9
judge votes on all 3 with-arm runs — the skill reliably asks two
calibration topics (what prompted this, and SQL/subquery experience)
instead of one, breaching `SKILL.md`'s "Ask one, not a quiz." See D3 and
Open.

Of the scored graders in the six teaching cases, 9 discriminate cleanly, 4
discriminate only weakly (the baseline lands them 2 of 3: `names-the-gotcha`,
`no-further-check`, `recap-is-one-item-per-step`, `issues-a-fresh-check`), 13
are inert (pass in both arms because bare Opus 5.5 already does the
behaviour), and 1 fails in the with arm (`no-extraneous-prose` — see D5). Inert graders cluster
mid-lesson: shaky 4/4, wrong-answer 3/4, next-means 3/4. On Opus 5.5, the
skill's measurable value is concentrated in the opening and first step —
not because the later behaviours don't matter, but because the baseline
already does most of them. See Open ("Graders that pass in both arms").

Keep a proportionate amount of caution anyway: the measured run-to-run
noise floor on a 3-run case is about ±0.20 (see `977aa3b`, where a closing
delta of +0.13 was judged inside that floor and left unpinned). A delta
smaller than that on any case below is not signal, and entries call this
out where it applies.

None of this changes Part 1's other problem: the *rationale* — the why
behind each decision — is reconstructed, not authored, regardless of how
solid the eval evidence under it is. See the note at the top of this file.

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

**Pinned by.** evals/opening/ (answer-before-route), run
`2026-09-25T05-03-33-276Z` (3 runs/arm, judge claude-opus-5-5): `PPP` with
/ `PPP` without. This grader passes in both arms — it shows the skill puts
the answer first, not that the baseline fails to. The case-level delta
(opening: 1.00 with / 0.25 without) is driven by D2 and D3's graders, not
this one.

## D2 — Route titles are claims

**Decision.** The route is a numbered list of 3–6 step titles, and each
title is a claim, not a topic: "The policy is AND-ed onto every scan," not
"Policy injection."

**Rejected.** Topic labels — faster to write, and they tell the reader
nothing about what they're about to learn.

**Cost.** Writing a route of claims costs real thought before any teaching
happens; a lazy route reverts to topic labels.

**Pinned by.** evals/opening/ (titles-are-claims, route-is-3-to-6-items),
run `2026-09-25T05-03-33-276Z` (3 runs/arm, judge claude-opus-5-5): both
graders `PPP` with / `FFF` without — a clean discriminator on each; the
baseline doesn't do this by default.

## D3 — Exactly one calibration question

**Decision.** The opening asks exactly one calibration question, then
stops and waits for the reply before step 1.

**Rejected.** A short quiz up front; and, at the other extreme, guessing
the reader's level and skipping the question entirely.

**Cost.** One extra round trip before any teaching starts.

**Pinned by.** evals/opening/ (asks-about-the-reader, calibration-is-one-ask,
no-step-yet), run `2026-09-25T05-03-33-276Z` (3 runs/arm, judge
claude-opus-5-5). `asks-about-the-reader` discriminates cleanly: `PPP`
with / `FFF` without — the calibration question is there and the baseline
doesn't ask one. `calibration-is-one-ask` and `no-step-yet` are
`arm: with-only` (unscored, contributing nothing to the delta) but are
still evidence of behaviour: `no-step-yet` is `PPP` — step 1 never leaks
into the opening — while `calibration-is-one-ask` is now `FFF`, unanimous
across all 9 judge votes in an audit of this run: the skill reliably asks
two calibration topics (what prompted this, and SQL/subquery experience)
in every with-arm run, not one. "Exactly one" is not landing; it is being
broken on a fixed, predictable pattern, not occasionally slipping. See
Open. (`one-calibration-question`, the grader this entry used to cite, was
split into these two in `a08a92c` and no longer exists.)

## D4 — Every step ends with a question you ask them

**Decision.** A step is not complete until the learner
answers a question that requires using the idea.

**Rejected.** Closing with "any questions?" — it asks the
learner to already know what they don't know, which is the
one thing they cannot do.

**Cost.** Roughly doubles the number of turns. Some users
find it slow; `next` is the escape hatch (see D7).

**Pinned by.** evals/first-step/ (check-requires-using-the-idea), run
`2026-09-25T05-03-33-276Z` (3 runs/arm, judge claude-opus-5-5): `PPP` with
/ `FFF` without — a clean discriminator, and one of the strongest in the
suite.

## D5 — Prose stays earned, not padded

**Decision.** Each step's prose stays tight and readable: no mannered
phrasing, no beating around the bush, no throat-clearing before the
point. A concept is never explained incompletely just to hit a count —
the author's ruling is that a step's length should be earned, not capped.

**Rejected.** A hard numeric word cap. `SKILL.md:59` still reads "≤150
words of prose. Hard budget," but per the author the cap's intent was
always tightness, not an arithmetic ceiling, and a long-but-earned step
should not have to break itself in two just to stay under a number.

**Cost.** Cutting narration without cutting content takes a real editing
pass — spotting a deletable sentence is harder than counting words.

**Pinned by.** evals/first-step/ (no-extraneous-prose), run
`2026-09-25T05-03-33-276Z` (3 runs/arm, judge claude-opus-5-5): `FFP` with
/ `PFF` without. This is the only scored grader in the suite that still
fails in a with-arm (`calibration-is-one-ask` also fails there but is
unscored — see D3), and it caps both arms rather than cleanly
discriminating — it is the sole reason first-step scores 0.89 rather than
1.00. The two failing with-arm replies carried pure narration — "We'll go
through it one idea at a time," "I'll tie each step to what you'd see in
your plan" — sentences a reader could delete with no loss of content,
which is exactly what the grader is written to catch: deletable
throat-clearing, ornament, hedging, restatement and tangents, while
explicitly passing a long-but-earned step.

**⚠ Skill and check disagree, deliberately** — the same situation as D6
and `SKILL.md:60`. `SKILL.md:59` still states a 150-word hard budget; the
check now in force (`no-extraneous-prose`, replacing
`step-prose-stays-tight` in `6c739f3`) judges tightness and freedom from
mannered phrasing instead, not a count. Until a refinement pass
reconciles them, this entry describes the author's ruling and the skill
still states the old numeric rule. `prose-under-150-words` and
`step-prose-stays-tight`, the predecessor graders that tried to enforce
the numeric budget and could not do it reliably, no longer exist and are
named here only as history.

## D6 — Illustrate the step, without crowding it

**Decision.** Each step shows its idea rather than only asserting it — a
diagram, a worked example with concrete values, or an analogy. More than
one is fine where they help; what is not fine is illustration that crowds
the step.

**Superseded.** This entry originally read "exactly one picture or one
worked example — not both, not three," and was pinned to a grader that
enforced it. The author has since relaxed the rule: more examples and
diagrams are welcome as long as readability does not suffer.

**Rejected.** The strict one-or-the-other form above, and at the other
extreme a step with nothing to look at.

**Cost.** "Crowding" is a judgement rather than a count, so this check can
no longer be decided mechanically.

**⚠ Skill and check disagree, deliberately.** `SKILL.md:60` still reads
"**Exactly one picture or one worked example.** Not both, not three." The
skill body is the author's to change and has not been changed; the grader
has. Until the refinement pass reconciles them, this entry describes the
author's ruling and the skill states the older rule.

**Pinned by.** evals/first-step/ (illustration-without-clutter), run
`2026-09-25T05-03-33-276Z` (3 runs/arm, judge claude-opus-5-5): `PPP` with
/ `FFF` without — a clean discriminator, where on the earlier Opus 5 run it
passed in both arms. The change is in the baseline model: bare Opus 5.5
answers this prompt with a markdown table comparing database engines, with
no diagram and no worked example carried through with values. The
description plays no part in that — the without arm runs with no plugin
loaded and never sees it.

A separate effect, in the *with* arm, belongs here because it concerns
diagrams. Before the description was cut from 87 to 69 words (`9d8bef5`,
removing "— or when they ask for a step-by-step explanation with diagrams,
examples, or pauses for questions"), the with-arm replies in
`wrong-answer-reteaches` drew a diagram in 6 of 6 runs across two runs in
which the skill never fired, against 0 of 6 without. After the cut, 0 of
3. The always-on description text alone had been steering output. See Open
for the same cut's cost to `next-means-one-step`'s natural trigger rate.

What the relaxation cost is worth recording too, because it is easy to
misread, and it is a separate point from the paragraph above. The strict
grader that preceded `illustration-without-clutter` was a clean
`PPP`/`FFF` discriminator on an earlier run, but it discriminated by
catching the *baseline* breaking a stylistic rule: bare Claude supplies a
diagram **and** a worked example. So first-step's previously perfect 0.00
baseline was partly rule-compliance rather than teaching quality, and
relaxing the rule moved that arm from 0.00 to 0.17 on that run. The delta
got smaller and more honest at the same time. This run's baseline moved
again, for the reason above, and the grader discriminates cleanly again —
for a different reason than the strict grader once did.

## D7 — `next` means one step, no commentary

**Decision.** `next` means one more step, delivered without commentary.

**Rejected.** Asking "are you sure you want to skip the check?" — it
punishes the reader for using the hatch that's supposed to be theirs to
use.

**Cost.** A reader can skip past a misunderstanding; that's their call to
make, not the skill's to prevent.

**Pinned by.** evals/first-step/ (escape-hatch-present), run
`2026-09-25T05-03-33-276Z`: `PPP` with / `FFF` without — a clean
discriminator. evals/next-means-one-step/ (escape-hatch-present,
exactly-one-step, advances-without-commentary, step-three-not-a-dump), run
`2026-09-25T05-03-33-276Z` (3 runs/arm, judge claude-opus-5-5):
`escape-hatch-present` `PPP` with / `FFF` without — the only one of the
four that still discriminates. `exactly-one-step`, `advances-without-commentary`
and `step-three-not-a-dump` are all `PPP` with / `PPP` without now — Opus
5.5's baseline already does all three, so they show the skill does this,
not that the baseline fails to.

This case now loads the skill by slash command
(`/what-the-heck:what-the-heck`) rather than a natural-language trigger —
see B10 for why, and for the canary evidence that the load is real.
`skill-fired` cannot see a slash-loaded skill and was removed from this
case's graders; the without arm receives the command as inert text and
opens by saying it isn't installed, which the audit of this run confirmed
changes no grade.

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
reteaches-from-a-new-angle), run `2026-09-25T05-03-33-276Z` (3 runs/arm,
judge claude-opus-5-5), with-arm a clean 1.00: `does-not-advance` `PPP`
with / `PPP` without and `does-not-affirm-the-wrong-answer` `PPP` with /
`PPP` without now both pass in both arms — Opus 5.5's baseline already
does these two. `issues-a-fresh-check` `PPP` with / `PPF` without —
discriminates, weakly. `reteaches-from-a-new-angle` is now `PPP` with /
`PPP` without: this grader was rewritten in `c68dacd` to judge content
rather than layout, after its previous version failed a with-arm reply
for reusing a quoted sketch's shape in a before/after diagram of real plan
nodes; under the rewritten version it no longer discriminates, but it also
no longer penalises a good reply for a formatting accident.

(An earlier version of this grader, under an even older rubric, failed
exactly one with-arm run in three because the prompt only summarised the
earlier explanation in one sentence, giving the judge nothing to compare
against; the prompt now quotes the teacher's step 2 in full, diagram
included, which the current content-not-layout rubric also relies on as
its reference text.)

This case now loads the skill by slash command, like the other
mid-lesson cases — see B10.

evals/shaky-reasoning-rechecks/ (does-not-advance,
does-not-simply-congratulate, names-the-specific-gap,
rechecks-before-moving-on), run `2026-09-25T05-03-33-276Z` (3 runs/arm,
judge claude-opus-5-5): all four graders are now `PPP` with / `PPP`
without. This case is fully inert on Opus 5.5 — bare Opus 5.5 already
rechecks shaky reasoning, names the specific gap, and does not simply
congratulate or advance past it — so its 1.00/1.00 case score is a finding
about where the skill's value is not, not a defect in the case. It too now
loads by slash command; see B10.

`does-not-affirm-the-wrong-answer`'s earlier rubric was keyword-brittle on
the literal word "exactly," testing vocabulary rather than behaviour; it
was rewritten in `7aa7414`. The scores above are under the rewritten
version.

## D9 — The close is the chain, then the one thing that bites

**Decision.** The close gives the whole chain back in about five lines,
one per step, then names the one thing most likely to bite them in
practice.

**Rejected.** A summary of topics covered — a table of contents after the
fact, not a chain.

**Cost.** Writing it well means having actually taught a chain rather than
a pile of facts.

**Pinned by.** evals/closing/ (names-the-gotcha, recap-is-one-item-per-step,
recap-is-easy-to-scan, causal-chain, no-further-check, no-new-step), run
`2026-09-25T05-03-33-276Z` (3 runs/arm, judge claude-opus-5-5). closing:
1.00 with / 0.80 without, every scored grader passing in the with-arm.
This case now loads the skill by slash command; see B10 for why and for
the earlier prompt-rewrite history that used to be needed just to get it
to fire at all.

`causal-chain`: `PPP` with / `PPP` without — passes in both arms. Kept
deliberately as a regression guard on the causal thread rather than as a
discriminator, by the author's decision. `recap-is-easy-to-scan`: `PPP`
with / `PPP` without — now also passes in both arms; Opus 5.5's baseline
recap is readable too. `names-the-gotcha`: `PPP` with / `PPF` without —
discriminates, weakly; the baseline lands it 2 of 3. `no-further-check`:
`PPP` with / `PFP` without — discriminates, weakly, same pattern.
`recap-is-one-item-per-step`: `PPP` with / `PPF` without — discriminates,
weakly.

`no-new-step` is new this run, `arm: with-only` (unscored) and `PPP`:
since the case now loads mid-lesson by slash command, the skill has to be
told not to smuggle a new step in under cover of the recap, and this run
it doesn't, in all three with-arm replies.

The grader that graded this decision at pilot time,
`recap-is-about-five-lines`, demanded four to six *lines* and passed 0 of
32 runs — in both arms, across five prompt variants, two descriptions and
two judge models. A check the baseline fails just as hard as the plugin
isn't measuring the plugin; it was capping both arms rather than
discriminating between them. It was rewritten and renamed
`recap-is-one-item-per-step` in `64433ae`, then rescoped to judge only the
recap (not the surrounding correction or gotcha note) in `07fe734`. It now
asks for one item per step, allows an item to run to a sentence or two, and
allows a closing sentence tying the chain together. The score above is
under that rewritten grader.

`causal-chain` carried the same disease, undetected, for longer. Its
criteria opened by asking for "a chain of about five lines, one per step,"
and that line count — not the causal thread the grader is named for — was
what the judge acted on. Two with-arm replies that were each five numbered
items, in taught order, each following from the one before, came back FAIL
and PASS. It now judges the thread alone, scoped to the recap, and the
length requirement lives in `recap-is-easy-to-scan` where it can be stated
generously. The cost of that split is visible above: with the line framing
gone, `causal-chain` passes in both arms, because the baseline's recap is
an ordered chain too. The line count was the only thing that ever made it
look like a discriminator, and it bought that appearance by failing good
replies two times in three.

Run `2026-09-25T05-03-33-276Z` is also the first on a correct prompt. Until `00eb7b1`,
`closing`'s restated step 5 claimed "A CTE referenced twice can be
evaluated twice", which is false for Postgres 12+ (a multiply-referenced
CTE is materialised by default and runs once). In one earlier Opus 5.5 run
the skill fired, caught the error, and re-taught step 5 with a check
instead of recapping a chain it knew to be wrong — exactly what D8 asks
for — and every recap grader failed it, because there was no recap. The
"correction paragraph before the recap" that earlier replies kept carrying
had the same cause.

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

---

## Part 2 — build and verification

Written with authority: these were decided in the design conversation, not
reconstructed after the fact.

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
sampled transcript.

**Rejected.** Resumed-session fixtures. They give exact fidelity to a real
conversation, but the harness forces any case with `context.history_file`
into the `with` arm alone (`if (r && e.context.history_file) return
["with"]`), which deletes the ablation delta on exactly the cases that
need it most — "it re-taught instead of advancing" is only evidence of the
skill working if bare Claude would have advanced instead. A sampled
transcript also runs to roughly 900 KB over about 60 top-level keys and
carries `ownerAccountUuid`, `ownerOrganizationUuid`, `cwd` and
`gitBranch`, all needing scrubbing on every regeneration.

**Cost.** The prompt describes the prior exchange instead of being it, so
a case can drift from what a real resumed session would actually contain.
A one-off hand-check against a genuinely resumed session was planned to
verify the gap is small; it has not been run yet, so this decision
currently rests on the design argument above, not on a checked comparison.

**Pinned by.** evals/first-step/, evals/closing/,
evals/wrong-answer-reteaches/, evals/next-means-one-step/,
evals/shaky-reasoning-rechecks/ — every multi-turn case in the suite. Each
one's score from run `2026-09-25T05-03-33-276Z` (judge claude-opus-5-5),
and the discrimination caveats that go with it, are given under its own
Part 1 entry (D4–D9), and the per-case table in the Evidence note names
the run. Read those before trusting any individual number.

Four of these five (all but first-step) now load the skill by slash
command rather than a natural-language trigger — see B10. That is a
separate decision from this one: B10 fixes how the skill gets loaded, so a
single-turn case can reproduce "loaded at turn 1, still loaded now"; B2 is
about how the *prior turns'* content reaches the prompt at all, restated
inline rather than replayed from a resumed-session fixture. Both apply
together in those four cases, and neither substitutes for the other.

One result belongs here rather than only under D8. The restated-context
design failed in a way worth recording: `wrong-answer-reteaches` restated
step 2's *claim* in a sentence, and a grader asking whether the reply
re-taught it differently had no earlier explanation to compare against.
Quoting the step in full fixed it. Inline restated context works, but it
has to restate what a grader actually needs to see, not just what the
learner needs to know.

It can also restate something false. `closing` taught, as its step 5, "A
CTE referenced twice can be evaluated twice", and the learner's answer
built on it. In Postgres 12+ a CTE referenced more than once is
materialised by default and runs once; double evaluation needs
`NOT MATERIALIZED`. Because the prompt is the whole of the prior lesson,
the error went unnoticed by everyone except the model under test (see D9).
Fixed in `00eb7b1`.

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
outside contributor by construction; and 21 LLM graders at roughly 95%
reliability each go red on good PRs often enough to teach everyone to
ignore the check.

**Cost.** Regressions in behaviour are caught by a human running the suite
before merge, not automatically by CI.

**Pinned by.** The lint job; the pre-merge command documented in the root
README.

## B5 — The port is lexical only

**Decision.** Porting the skill into this plugin changed four identifiers
and nothing else — the `description` included.

**Rejected.** Fixing the too-broad description during the port. The suite
is written by the same person editing the skill; a suite written to match
edits just made would only confirm the author is self-consistent, not
that the skill behaves.

**Cost.** One extra iteration once the suite finds a real problem — cheap,
because a passing negative-trigger case is a short run.

**Pinned by.** evals/opening/ and the three trigger cases
(evals/no-trigger-task-ask/, evals/no-trigger-mid-implementation/,
evals/no-trigger-explain-and-do/), which grade rules the author wrote, not
rules edited to pass. All four now have evidence from run
`2026-09-25T05-03-33-276Z` (judge claude-opus-5-5): opening scores 1.00
with / 0.25 without; the three trigger cases each score 1.00 with / 1.00
without, `skill-did-not-fire` passing in every arm. The one red this
lexical-only port has produced — the description over-triggering on a
task request that borrows its own vocabulary — was found on
`no-trigger-explain-and-do` and then fixed; see B6.

## B6 — The trigger excludes task requests

**Decision.** The skill's trigger is narrow: a request to perform a task
does not fire the skill, even when it carries an "I don't get this,
explain as you go" rider.

**Rejected.** Leaving the description broad and letting the skill fire on
"how do I add an index to this table?"

**Cost.** A genuine "explain this to me" phrased as a task request may now
go unanswered by the skill.

**Pinned by.** evals/no-trigger-task-ask/,
evals/no-trigger-mid-implementation/, evals/no-trigger-explain-and-do/ —
the last one is the case that actually stresses the boundary (see below).
This entry now has both halves of its evidence, red and green, both from a
Sonnet judge and both reproducible from the case directory.

The 1-run Haiku pilot found no over-triggering on the two prompts that
existed at the time — `skill-did-not-fire` passed in every arm of both
`no-trigger-task-ask` and `no-trigger-mid-implementation` — but neither
prompt used any of the description's own trigger vocabulary ("explain X to
me," "walk me through X," "I don't get X"), so a clean pass proved little
either way. `evals/no-trigger-explain-and-do/` was written afterward
specifically to test the boundary: its prompt — "I don't really get
indexes — can you add one to this table and explain as you go?" —
deliberately uses that vocabulary while still being a task request.

It has now run: 3 runs, both arms, **Sonnet** as the judge, $0.78, 84
seconds (run `2026-09-21T01-18-12-741Z`). The result is the red the spec
predicted and the pilot couldn't produce — the trigger, as currently
worded, is too broad:

```
no-trigger-explain-and-do   with 0.00   without 1.00   Δ -1.00   (6 runs)
  with-arm, all 3 runs:    ✗ skill-did-not-fire        Skill called 1x (expected 0..0)
                            ✗ explains-while-doing-the-task   judge votes: FAIL FAIL FAIL
  without-arm, all 3 runs: ✓ skill-did-not-fire        Skill called 0x (expected 0..0)
                            ✓ explains-while-doing-the-task   judge votes: PASS PASS PASS
```

The skill fired on all three with-arm runs. When it fired,
`explains-while-doing-the-task` failed 3/3 under the Sonnet judge — the
lesson took over instead of the task getting done and explained in place.
The same rubric passed 3/3 in the without-arm, so the rubric is well
calibrated: it passes a good direct answer and fails a lesson takeover.
Δ −1.00 is the largest effect measured anywhere in this suite, and it is
harm, not benefit.

**The green after.** The `description` was then narrowed additively in
`cccb571` — two "Not for…" clauses, the skill body untouched — and the case
went green when the full 9-case suite ran (run `2026-09-21T02-09-29-432Z`,
3 runs per arm, Sonnet judge, $8.38, 596 seconds). The numbers quoted below
are from a later, stronger run of the same three trigger cases (run
`2026-09-21T04-03-19-502Z`, 3 runs per arm, Sonnet judge, $1.91, 217
seconds), and they are the ones to cite, for a reason that matters: by then
the description had been cut from 140 words to 87 in `c344426`, which
removed a worked example that had been close to word-for-word the prompt of
this very case. The first green could have been the model pattern-matching
the example; this one cannot be, so it shows the rule generalising.

```
no-trigger-explain-and-do   with 1.00   without 1.00   Δ 0.00   (6 runs)
  with-arm, all 3 runs:    ✓ skill-did-not-fire        Skill called 0x (expected 0..0)
                            ✓ explains-while-doing-the-task   judge votes: PASS PASS PASS
  without-arm, all 3 runs: ✓ skill-did-not-fire        Skill called 0x (expected 0..0)
                            ✓ explains-while-doing-the-task   judge votes: PASS PASS PASS
```

The prompt that fired the skill 3/3 before now fires it 0/3, and the task
gets done and explained in place in every run of both arms. Δ −1.00 → 0.00.
This entry has both halves of its evidence, each from a judge model of its
own era, and neither was invented. The fix still holds under the current
pinned run (`2026-09-25T05-03-33-276Z`, judge claude-opus-5-5): 1.00 with
/ 1.00 without, `skill-did-not-fire` `PPP`/`PPP` — see the Evidence note.

**What it cost.** Nothing measured, as it turns out. An earlier version of
this entry blamed the `closing` case's 0/3 firing rate on this narrowing —
that conclusion rested on a single pilot run and was wrong. The settled
diagnosis (see D9 and Open): `closing`'s prompt stated the lesson was over
and requested nothing, and every trigger this description names is
request-shaped, so nothing in the prompt matched, with or without the
narrowing. Rewriting the prompt to actually ask for the recap (`977aa3b`)
fires the skill 3/3 with no skill named and no baseline contamination. This
narrowing did not cost `closing` its trigger.

## B7 — "Read the code first" ships unpinned

**Decision.** "When the subject is in this repo, read the code before
step 1" is deliberately unpinned in v1.

**Rejected.** Writing the ninth case now. It needs a committed fixture
repo plus `context.add_dirs`, then a `tool_used` grader (`Read`, `min: 1`)
and an LLM grader for citing a real path and line number — a new class of
asset for one rule.

**Cost.** The rule can drift without the suite noticing.

**Pinned by.** Unpinned, by decision. See Open.

## B8 — Judge model history: Haiku, then Sonnet

**Decision (historical).** Judge model: Haiku for the original pilot run,
`--judge-model sonnet` for the 3-run suite that came next and was, at the
time, the run whose verdict was trusted. The judge has since moved again,
to claude-opus-5-5 — see B9, which is the current, pinned decision.

**Rejected.** Sonnet throughout from the start — no cheap run to catch
wording bugs in the rubrics before paying for judged runs three times over
on a stronger, pricier model.

**Cost.** Sonnet cost more per judged run than Haiku; that expense was
deliberately deferred to the run that counted rather than spent on the
pilot.

**Pinned by.** Historical only. The pilot-vs-Sonnet comparison this entry
used to carry, grader by grader, is not being maintained — the author's
call: it did its job catching early judge-quality misses, and the judge
has moved on again since. Its finding still stands as the reason a
stronger judge mattered at all: of eight compared graders, five were clean
judge misses under Haiku that resolved under Sonnet, one (the word-count
grader that later became `no-extraneous-prose` — see D5) did not resolve
and was a real rule-compliance gap rather than a judge error, and two were
confounded by rubric rewrites between the two runs, so their movement
couldn't be attributed to the judge alone. See B9 for the judge decision
now in force.

## B9 — Pin the model under test and the judge

**Decision.** The model under test is pinned to claude-opus-5-5 in every
case (`218d252`); lint now refuses a case with no pinned model. The judge
is claude-opus-5-5 too, passed as a full model ID (`241ab80`), in the root
README's documented eval command and in `eval.yml` — both previously
passed no judge flag at all, which meant Haiku by the tool's default.

**Rejected.** Leaving cases unpinned, letting them run on the CLI's
built-in default model. Before this decision, "unpinned" meant "whatever
model the CLI defaults to" — the eval sandbox never reads the user's
`settings.json` — and the CLI moved 2.1.278 -> 2.1.280 between the runs
this log used to cite, moving its `opus` alias from claude-opus-5 to
claude-opus-5-5 along with it. Every number pinned before this decision is
from that earlier, unverified era and is superseded; see the Evidence
note.

**Cost.** The judge costs more per run than the Sonnet judge it replaces;
the author accepted that on the ruling that the grader should be the more
capable model. The model under test costs no more than the Opus default it
replaced — its sessions ran cheaper. Judge and model-under-test
being the same model is a self-preference risk worth naming on its own —
the judge could favor output shaped like its own — but both arms share
that model, so the risk mostly cancels out of the delta even though it
does not cancel out of either arm's absolute score.

**Pinned by.** The lint rule that now refuses an unpinned case;
`aggregate-result.json` for run `2026-09-25T05-03-33-276Z`, which records
`model: claude-opus-5-5` on every case (unpinned runs recorded none); and
the drift this decision responds to: the CLI's `opus` alias changing
underneath every previously-unpinned case between 2.1.278 and 2.1.280,
with no run ever recording which physical model it actually hit.

## B10 — Load the skill by slash command in mid-lesson cases

**Decision.** The four mid-lesson cases — `next-means-one-step`,
`shaky-reasoning-rechecks`, `wrong-answer-reteaches`, `closing` — open
their prompt with `/what-the-heck:what-the-heck` instead of relying on a
natural-language trigger.

**Rejected.** Triggering these cases the same way as `opening` and
`first-step`. On claude-opus-5-5, no prompt wording fired the skill
reliably mid-lesson: four wordings were tried — a plain statement, a plain
request, the description's own "walk me through" phrase, and restating
"what the heck is a CTE?" — and the best of them reached about 1 in 3. In real
use the skill loads once, at turn 1, and stays loaded for the rest of the
session; a single-turn eval case can only reproduce "already loaded" by
loading it deterministically, not by re-rolling the trigger dice on every
case.

**Cost.** `skill-fired` (`tool_used: Skill`) cannot see a slash-loaded
skill, so it was removed from these four cases' graders — the suite now
splits into cases that test triggering (`opening`, `first-step`, the
three `no-trigger-*` cases) and cases that test behaviour once loaded (the
four above). The without arm receives the same slash command as inert
text and opens by saying it isn't installed; an audit of this run found
that this changes no grade, and `advances-without-commentary` is told
explicitly to ignore it.

**Pinned by.** A canary test: a throwaway copy of the plugin whose
`SKILL.md` body told the model to end every reply with a nonsense token,
graded by regex, no judgement involved. With the slash command in the prompt,
the token appeared in 3 of 3 with-arm replies and 0 of 3 without-arm
replies. The same prompt without the command: 1 of 3 with-arm replies, 0 of
3 without —
matching the roughly-one-in-three natural firing rate found elsewhere.
This canary run was a scratchpad experiment and is not committed; it is
described here so it can be reproduced, not cited as a committed asset. The
behaviour this decision buys is pinned by run `2026-09-25T05-03-33-276Z`,
in which all four slash-loaded cases score 1.00 in the with arm.
See D7, D8 and D9 for the cases this changed, and Open for the natural
trigger regression it surfaces on `next-means-one-step`.

---

## Open

| Item | Open because | Resolved by |
|---|---|---|
| A ninth eval case for "read the code before step 1" (B7) | Needs a committed fixture repo and `context.add_dirs`; deliberately deferred | A later pass, if a run suggests the rule drifts |
| Part 1 of this log | The rationale is reconstructed, not authored | The author's review pass |
| Closing-step brevity: the "what will bite you" note | As of the current run (`2026-09-25T05-03-33-276Z`), still no grader in the suite checks this — `recap-is-one-item-per-step` was rescoped in `07fe734` to judge only the recap, not the gotcha note, and the new `no-new-step` grader (see D9) checks a different thing (no smuggled step, not brevity), so the pilot's finding (the note running to about four paragraphs of fresh teaching) hasn't been re-tested since | A refinement pass the author has already accepted ("we'll make the closing more brief"), and a grader that checks the gotcha note's length now that none does |
| Graders that pass in both arms | 13 of the 27 scored graders across the six teaching cases: `opening/answer-before-route`; `next-means-one-step/exactly-one-step`, `advances-without-commentary`, `step-three-not-a-dump`; `closing/causal-chain`, `recap-is-easy-to-scan`; `wrong-answer-reteaches/does-not-advance`, `does-not-affirm-the-wrong-answer`, `reteaches-from-a-new-angle`; `shaky-reasoning-rechecks/does-not-advance`, `does-not-simply-congratulate`, `names-the-specific-gap`, `rechecks-before-moving-on`. Each is a finding about where the skill's value is not, rather than a defect in the grader — bare Opus 5.5 already does all of these — but it means those 13 contribute nothing to any delta. Of the remaining 14, 9 discriminate cleanly, 4 only weakly (`names-the-gotcha`, `no-further-check`, `recap-is-one-item-per-step`, `issues-a-fresh-check` — the baseline lands each 2 of 3), and 1 fails in the with arm (`no-extraneous-prose`, see D5). Note the mechanism: the restated-context prompts (B2) hand the baseline an explicit teaching frame, so the without-arm is not a naive baseline, and in the four slash-command cases (B10) the baseline sees the command only as plain text, with no skill behind it | A decision per grader, not a sweep. Marking the 13 `arm: with-only` would lift the deltas substantially and would be dishonest, since it works by hiding that the baseline is good. Keeping them scored is the current call |
| "Ask one, not a quiz" — the calibration rule is not landing | `opening/calibration-is-one-ask` is `FFF` on the current run, unanimous across all 9 judge votes in an audit: the skill reliably asks two calibration topics (what prompted this, and SQL/subquery experience) in every with-arm run, not one. This is no longer a maybe — it is a confirmed, repeatable skill-compliance gap, not a grader bug, and it holds under an adversarial refutation pass | The author deciding which way it goes: make the rule bite harder, or accept that motivation-plus-level in one compact breath is good calibration rather than a quiz |
| `next-means-one-step`'s natural trigger rate fell after the description cut | The 87 -> 69 word cut (`9d8bef5`) removed the clause ending "...or when they ask for a step-by-step explanation with diagrams, examples, or pauses for questions." `next-means-one-step`'s prompt ends with "next," and its natural firing rate on claude-opus-5-5 fell from 3/3 to 1/3 with the same prompt once that clause was gone — a real regression in triggering, separate from the case's current slash-command loading (B10), which was adopted for a different reason (mid-lesson firing was unreliable everywhere, not just after this cut) | The author deciding whether to restore a short step-by-step clause to the description, weighed against the over-triggering risk narrowed by B6 |
| The skill states a numeric word budget; the check now grades tightness instead | `SKILL.md:59` still reads "≤150 words of prose. Hard budget," but the current grader (`no-extraneous-prose`, replacing `step-prose-stays-tight` in `6c739f3`) doesn't count words at all — it judges deletable narration, and explicitly passes a long step that earns its length. It is the only grader anywhere in the suite that still fails in a with-arm (`FFP` this run), on replies carrying pure narration ("We'll go through it one idea at a time"). Whether the 150-word number itself is still the rule, or was superseded by the tightness standard, hasn't been said outright. See D5 | An author ruling: keep 150 as a real ceiling and treat any overrun as a skill defect, or drop the number from `SKILL.md:59` in favor of the tightness standard the grader already enforces |
| The skill says one illustration, the grader allows several | The author relaxed the rule (D6) but `SKILL.md:60` still reads "**Exactly one picture or one worked example.** Not both, not three." The skill body is the author's to change and has not been | The refinement pass, reconciling `SKILL.md:60` with D6 |
| The B2 resumed-session hand-check | Planned as a one-off comparison against a genuinely resumed session; not yet performed | Running it and recording the verdict in B2 |
| Verifying the install on the published path | The personal copy at `~/.claude/skills/what-the-heck/` has been deleted and the plugin installs cleanly from a local-path marketplace, but `origin/main` still holds only `LICENSE`, so the spec's `/plugin marketplace add sskirby/ai-tooling` cannot resolve yet | Merging the pull request, then adding the marketplace by its GitHub name and running one case against that install |
