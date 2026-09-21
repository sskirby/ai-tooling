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

Every entry below that cites an eval case is now backed by a 3-run-per-arm
suite, judged by Sonnet, for all nine cases — each cited run postdates both
the shipped 87-word skill description (`c344426`) and that case's own last
file change, so every number below grades the tree as it ships. The
original 1-run Haiku pilot (`2026-09-20T23-59-05-792Z`, $2.15, eight cases —
`no-trigger-explain-and-do` didn't exist yet) is superseded everywhere it
was cited for a case score. It survives only in B8, where it is the
baseline of a judge-model comparison, not current evidence.

Where each case stands, freshest run per case, `with` score / `without`
score / delta:

| case | with | without | Δ | run |
|---|---|---|---|---|
| first-step | 0.89 | 0.00 | +0.89 | `2026-09-21T05-20-55-941Z` |
| opening | 1.00 | 0.25 | +0.75 | `2026-09-21T20-05-06-263Z` |
| next-means-one-step | 1.00 | 0.33 | +0.67 | `2026-09-21T04-58-08-088Z` |
| closing | 0.83 | 0.25 | +0.58 | `2026-09-21T16-46-23-241Z` |
| wrong-answer-reteaches | 0.92 | 0.50 | +0.42 | `2026-09-21T16-47-57-966Z` |
| shaky-reasoning-rechecks | 1.00 | 0.58 | +0.42 | `2026-09-21T16-49-53-988Z` |
| no-trigger-explain-and-do | 1.00 | 1.00 | 0.00 | `2026-09-21T04-03-19-502Z` |
| no-trigger-mid-implementation | 1.00 | 1.00 | 0.00 | `2026-09-21T04-03-19-502Z` |
| no-trigger-task-ask | 1.00 | 1.00 | 0.00 | `2026-09-21T04-03-19-502Z` |

The mean delta is **+0.62 across the six teaching cases** and **+0.41
across all nine**. Always say which population a mean covers: the three
`no-trigger-*` cases score a correct 0.00 by design — the skill must not
fire on those prompts and it does not — so averaging them in drags the
figure down for a reason that is a pass, not a failure.

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
`2026-09-21T20-05-06-263Z` (3 runs/arm, Sonnet judge): `PPP` with / `PPP`
without. This grader passes in both arms — it shows the skill puts the
answer first, not that the baseline fails to. The case-level delta
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
run `2026-09-21T20-05-06-263Z` (3 runs/arm, Sonnet judge): both graders
`PPP` with / `FFF` without — a clean discriminator on each; the baseline
doesn't do this by default.

## D3 — Exactly one calibration question

**Decision.** The opening asks exactly one calibration question, then
stops and waits for the reply before step 1.

**Rejected.** A short quiz up front; and, at the other extreme, guessing
the reader's level and skipping the question entirely.

**Cost.** One extra round trip before any teaching starts.

**Pinned by.** evals/opening/ (asks-about-the-reader, calibration-is-one-ask,
no-step-yet), run `2026-09-21T20-05-06-263Z` (3 runs/arm, Sonnet judge).
`asks-about-the-reader` discriminates cleanly: `PPP` with / `FFF` without —
the calibration question is there and the baseline doesn't ask one.
`calibration-is-one-ask` and `no-step-yet` are `arm: with-only` (unscored,
contributing nothing to the delta) but are still evidence of behaviour:
`no-step-yet` is `PPP` — step 1 never leaks into the opening — while
`calibration-is-one-ask` is `PPF`, meaning one of the three with-arm runs
asked more than one question, so "exactly one" isn't fully landing yet.
(`one-calibration-question`, the grader this entry used to cite, was split
into these two in `a08a92c` and no longer exists.)

## D4 — Every step ends with a question you ask them

**Decision.** A step is not complete until the learner
answers a question that requires using the idea.

**Rejected.** Closing with "any questions?" — it asks the
learner to already know what they don't know, which is the
one thing they cannot do.

**Cost.** Roughly doubles the number of turns. Some users
find it slow; `next` is the escape hatch (see D7).

**Pinned by.** evals/first-step/ (check-requires-using-the-idea), run
`2026-09-21T05-20-55-941Z` (3 runs/arm, Sonnet judge): `PPP` with / `FFF`
without — a clean discriminator. This grader was one of the Haiku pilot's
judge-quality misses (Haiku scored it `F`); the Sonnet re-run resolves it
as landing behaviour, not a judge artefact.

## D5 — 150 words of prose, hard budget

**Decision.** Each step carries a hard budget of 150 words of prose.

**Rejected.** Letting a step run long when the idea is "nearly" one idea —
that's exactly how two ideas end up stacked into one step.

**Cost.** Some ideas that felt like one step have to split into two.

**Pinned by.** evals/first-step/ (prose-under-150-words), run
`2026-09-21T05-20-55-941Z` (3 runs/arm, Sonnet judge): `FPF` with / `FFF`
without. Two things are true at once here, and neither should be flattened
into the other. The rule is not reliably landing: it fails 2 of 3 with-arm
runs under a stronger judge, and it's the sole reason first-step scores
0.89 rather than 1.00. But it does discriminate — the without-arm fails
3/3 too, so the check is measuring something the baseline doesn't do.
Complicating both readings: the run that PASSED had a *longer* total reply
than the two that failed, which is evidence the grader is doing arithmetic
on a filtered slice of the text rather than a stable count — a shaky
instrument, not just an unsettled rule. Pin this as unsettled on both
counts; it is neither vindicated nor broken yet.

## D6 — One picture or one example, never both

**Decision.** Each step carries exactly one picture or one worked example
— not both, not three.

**Rejected.** Using both, which reads as thorough but doubles what the
reader has to hold in their head at once.

**Cost.** Sometimes the weaker of two good illustrations has to be cut.

**Pinned by.** evals/first-step/ (one-picture-or-one-example), run
`2026-09-21T05-20-55-941Z` (3 runs/arm, Sonnet judge): `PPP` with / `FFF`
without — a clean discriminator. Also one of the pilot's judge-quality
misses (Haiku scored it `F`); Sonnet resolves it as landing behaviour.

## D7 — `next` means one step, no commentary

**Decision.** `next` means one more step, delivered without commentary.

**Rejected.** Asking "are you sure you want to skip the check?" — it
punishes the reader for using the hatch that's supposed to be theirs to
use.

**Cost.** A reader can skip past a misunderstanding; that's their call to
make, not the skill's to prevent.

**Pinned by.** evals/first-step/ (escape-hatch-present), run
`2026-09-21T05-20-55-941Z`: `PPP` with / `FFF` without — a clean
discriminator. evals/next-means-one-step/ (escape-hatch-present,
exactly-one-step, advances-without-commentary, step-three-not-a-dump), run
`2026-09-21T04-58-08-088Z` (3 runs/arm, Sonnet judge):
`escape-hatch-present` `PPP` with / `FFF` without; `exactly-one-step` `PPP`
with / `PPF` without; `advances-without-commentary` `PPP` with / `FPF`
without; `step-three-not-a-dump` `PPP` with / `PFF` without. All four
discriminate, though `exactly-one-step` only weakly — the baseline lands it
2 of 3 runs anyway. `step-three-not-a-dump` was one of the pilot's
judge-quality misses, now resolved under Sonnet. `advances-without-commentary`'s
rubric was rewritten between the pilot and this run (`0aad611`), so only
this current Sonnet number should be cited — its pilot score isn't
comparable.

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
reteaches-from-a-new-angle), run `2026-09-21T16-47-57-966Z` (3 runs/arm,
Sonnet judge): `does-not-advance` `PPP` with / `FFF` without —
discriminates. `does-not-affirm-the-wrong-answer` `PPP` with / `PPP`
without and `issues-a-fresh-check` `PPP` with / `PPP` without both pass in
both arms: they show the skill does this, not that the skill does it and
the baseline doesn't. `reteaches-from-a-new-angle` `FPP` with / `FFF`
without — discriminates, though one with-arm run itself failed to reteach
from a new angle.

evals/shaky-reasoning-rechecks/ (does-not-advance,
does-not-simply-congratulate, names-the-specific-gap,
rechecks-before-moving-on), run `2026-09-21T16-49-53-988Z` (3 runs/arm,
Sonnet judge): `does-not-advance` `PPP` with / `FFF` without —
discriminates. `does-not-simply-congratulate` `PPP` with / `PPP` without
and `names-the-specific-gap` `PPP` with / `PPP` without both pass in both
arms — same caveat as above, and both rubrics were rewritten after the
pilot (`7aa7414`, `6deb7c8`), so their pilot scores aren't comparable to
these. `rechecks-before-moving-on` `PPP` with / `PFF` without —
discriminates; one of the pilot's judge-quality misses, now resolved under
Sonnet.

`does-not-affirm-the-wrong-answer`'s earlier rubric was keyword-brittle on
the literal word "exactly," testing vocabulary rather than behaviour; it
was rewritten in `7aa7414`. The score above is under the rewritten
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
causal-chain, no-further-check), run `2026-09-21T16-46-23-241Z` (3
runs/arm, Sonnet judge) — the first trustworthy run of this case, reached
only after five prompt rewrites just to get the skill to fire at all (see
B6 and Open). closing: 0.83 with / 0.25 without.

`names-the-gotcha`: `PPP` with / `FFF` without — discriminates cleanly.
`recap-is-one-item-per-step`: `PPP` with / `FFP` without — discriminates.
`causal-chain`: `FFP` with / `FFF` without — weak; it fails two of three
with-arm runs too, so treat it as marginal evidence at best.
`no-further-check`: `PPP` with / `PPF` without — discriminates, weakly (the
baseline avoids a redundant check in 2 of 3 runs anyway).

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
one's freshest 3-run Sonnet score, and the discrimination caveats that go
with it, are given under its own Part 1 entry (D4–D9); read those before
trusting any individual number.

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
rules edited to pass. All four now have 3-run Sonnet evidence: opening
scores 1.00 with / 0.25 without (run `2026-09-21T20-05-06-263Z`); the three
trigger cases each score 1.00 with / 1.00 without, `skill-did-not-fire`
passing in every arm of every run (run `2026-09-21T04-03-19-502Z`). The one
red this lexical-only port has produced — the description over-triggering
on a task request that borrows its own vocabulary — was found on
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
This entry has both halves of its evidence, each from a Sonnet judge, and
neither was invented.

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

## B8 — Haiku pilot, Sonnet for the run that counts

**Decision.** Judge model: Haiku for the pilot run, `--judge-model sonnet`
for the full 3-run suite whose verdict is trusted.

**Rejected.** Sonnet throughout from the start — no cheap run to catch
wording bugs in the rubrics before paying for judged runs three times over
on a stronger, pricier model.

**Cost.** Sonnet costs more per judged run than Haiku; that expense is
deliberately deferred to the run that counts rather than spent on the
pilot.

**Pinned by.** The pilot-vs-Sonnet comparison below, grader by grader,
checked against each grader's current text on disk
(`evals/*/graders/*.md`, or inline in `case.yaml`):

| case/grader | Haiku pilot | Sonnet (current) | verdict |
|---|---|---|---|
| first-step/check-requires-using-the-idea | F | PPP | clean judge miss, resolved |
| first-step/one-picture-or-one-example | F | PPP | clean judge miss, resolved |
| first-step/prose-under-150-words | F | FPF | not a judge miss — still fails 2 of 3 |
| next-means-one-step/step-three-not-a-dump | F | PPP | clean judge miss, resolved |
| next-means-one-step/advances-without-commentary | F | PPP | confounded — rubric rewritten in `0aad611` |
| shaky-reasoning-rechecks/rechecks-before-moving-on | F | PPP | clean judge miss, resolved |
| shaky-reasoning-rechecks/does-not-simply-congratulate | F | PPP | confounded — rubric rewritten in `7aa7414` |
| wrong-answer-reteaches/issues-a-fresh-check | F | PPP | clean judge miss, resolved |

Five of these are clean judge misses that resolve under Sonnet; one
(`prose-under-150-words`, see D5) does not resolve — it still fails 2 of 3
with-arm runs under the stronger judge; two are confounded, because their
rubrics were rewritten between the pilot and the Sonnet run, so their
movement can't be attributed to the judge alone. That's five of eight
clean resolutions, not eight — an earlier tally of "eight judge-quality
misses" lived only in a gitignored controller ledger and can't be checked
from this repo. The decision itself still holds: a better judge changed
most of these verdicts, which is why `--judge-model sonnet` is reserved
for the run that counts.

---

## Open

| Item | Open because | Resolved by |
|---|---|---|
| A ninth eval case for "read the code before step 1" (B7) | Needs a committed fixture repo and `context.add_dirs`; deliberately deferred | A later pass, if a run suggests the rule drifts |
| Part 1 of this log | The rationale is reconstructed, not authored | The author's review pass |
| Closing-step brevity: the "what will bite you" note | Under the current Sonnet run (`2026-09-21T16-46-23-241Z`), no grader in the suite checks this anymore — `recap-is-one-item-per-step` was rescoped in `07fe734` to judge only the recap, not the gotcha note, so the pilot's finding (the note running to about four paragraphs of fresh teaching) hasn't been re-tested since | A refinement pass the author has already accepted ("we'll make the closing more brief"), and a grader that checks the gotcha note's length now that none does |
| `closing`'s `causal-chain` grader discriminates only weakly | `FFP` with / `FFF` without on the current Sonnet run — it fails two of three with-arm runs too, so it's marginal evidence rather than a settled discriminator | More runs, or a rubric pass on `causal-chain` if it doesn't strengthen |
| "Ask one, not a quiz" — whether the calibration rule is right | `opening/calibration-is-one-ask` is `PPF` on the current run and was failing 3/3 under the grader it replaced: the skill regularly asks its two named example questions ("what prompted this?" *and* "how much of X do you already work with?") rather than one. Combining the two most recent runs, 4 of 6 with-arm replies raise a second topic. The rule is stated in the skill and lands about a third of the time. This is the one place an eval has found a skill-compliance gap rather than a grader bug | The author deciding which way it goes: make the rule bite harder, or accept that motivation-plus-level in one compact breath is good calibration rather than a quiz |
| `first-step/prose-under-150-words` is unsettled on two axes at once | It fails 2 of 3 with-arm runs under Sonnet and is the sole reason `first-step` scores 0.89 rather than 1.00 — but the run that PASSED had a longer total reply than the two that failed, which says the grader's word count is not stable. So the rule may not be landing *and* the instrument may not be able to tell. See D5 | Either a grader that counts deterministically rather than asking a judge to do arithmetic on a filtered slice of the message, or an author ruling that 150 words is the wrong budget |
| The B2 resumed-session hand-check | Planned as a one-off comparison against a genuinely resumed session; not yet performed | Running it and recording the verdict in B2 |
| Verifying the install on the published path | The personal copy at `~/.claude/skills/what-the-heck/` has been deleted and the plugin installs cleanly from a local-path marketplace, but `origin/main` still holds only `LICENSE`, so the spec's `/plugin marketplace add sskirby/ai-tooling` cannot resolve yet | Merging the pull request, then adding the marketplace by its GitHub name and running one case against that install |
