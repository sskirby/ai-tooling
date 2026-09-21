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

Most entries below that cite an eval case are backed, right now, by a
single pilot run: 1 run per case, both arms, Haiku as the judge, $2.15
total, across the eight cases that existed when it ran. That is much
thinner than the 3-run `--judge-model sonnet` suite this plugin is meant to
ship on — read every pilot score below as a first signal, not a verdict.
Where a case's graders turned up in the pilot's judge-quality triage — a
weak Haiku judge missing behaviour that was actually there — the entry
says so, because that grader's verdict is not yet trustworthy.

The ninth case, `no-trigger-explain-and-do`, was added after the pilot and
ran separately: 3 runs, both arms, **Sonnet** as the judge, $0.78. Do not
merge its numbers into the pilot's — different case count, different
judge, different run count. See B6.

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

**Pinned by.** evals/opening/ (answer-before-route). 1-run Haiku pilot:
opening scored 1.00 with the skill, 0.50 without.

## D2 — Route titles are claims

**Decision.** The route is a numbered list of 3–6 step titles, and each
title is a claim, not a topic: "The policy is AND-ed onto every scan," not
"Policy injection."

**Rejected.** Topic labels — faster to write, and they tell the reader
nothing about what they're about to learn.

**Cost.** Writing a route of claims costs real thought before any teaching
happens; a lazy route reverts to topic labels.

**Pinned by.** evals/opening/ (titles-are-claims, route-is-3-to-6-items).
Same 1-run Haiku pilot as D1: opening 1.00 with / 0.50 without.

## D3 — Exactly one calibration question

**Decision.** The opening asks exactly one calibration question, then
stops and waits for the reply before step 1.

**Rejected.** A short quiz up front; and, at the other extreme, guessing
the reader's level and skipping the question entirely.

**Cost.** One extra round trip before any teaching starts.

**Pinned by.** evals/opening/ (one-calibration-question, no-step-yet).
1-run Haiku pilot: opening 1.00 with / 0.50 without.

## D4 — Every step ends with a question you ask them

**Decision.** A step is not complete until the learner
answers a question that requires using the idea.

**Rejected.** Closing with "any questions?" — it asks the
learner to already know what they don't know, which is the
one thing they cannot do.

**Cost.** Roughly doubles the number of turns. Some users
find it slow; `next` is the escape hatch (see D7).

**Pinned by.** evals/opening/, evals/first-step/. 1-run Haiku pilot: opening
1.00 with / 0.50 without; first-step 0.50 with / 0.00 without.
first-step's `check-requires-using-the-idea` grader was one of the pilot's
eight judge-quality misses — the judge failed it 3/3 on behaviour triage
called correct — so treat that grader's verdict as unsettled until the
Sonnet re-run.

## D5 — 150 words of prose, hard budget

**Decision.** Each step carries a hard budget of 150 words of prose.

**Rejected.** Letting a step run long when the idea is "nearly" one idea —
that's exactly how two ideas end up stacked into one step.

**Cost.** Some ideas that felt like one step have to split into two.

**Pinned by.** evals/first-step/ (prose-under-150-words). 1-run Haiku
pilot: first-step 0.50 with / 0.00 without. This grader was one of the
pilot's eight judge-quality misses: triage hand-counted the actual reply at
~97 words against the 150 limit and found it compliant, but the judge
failed it 3/3. Left alone deliberately — the rubric is right, the judge is
weak; the fix is a stronger judge, not a rewritten rubric.

## D6 — One picture or one example, never both

**Decision.** Each step carries exactly one picture or one worked example
— not both, not three.

**Rejected.** Using both, which reads as thorough but doubles what the
reader has to hold in their head at once.

**Cost.** Sometimes the weaker of two good illustrations has to be cut.

**Pinned by.** evals/first-step/ (one-picture-or-one-example). Same 1-run
Haiku pilot as D5, and this grader was also one of the pilot's eight
judge-quality misses — left alone for the same reason.

## D7 — `next` means one step, no commentary

**Decision.** `next` means one more step, delivered without commentary.

**Rejected.** Asking "are you sure you want to skip the check?" — it
punishes the reader for using the hatch that's supposed to be theirs to
use.

**Cost.** A reader can skip past a misunderstanding; that's their call to
make, not the skill's to prevent.

**Pinned by.** evals/first-step/ (escape-hatch-present),
evals/next-means-one-step/. 1-run Haiku pilot: first-step 0.50 with / 0.00
without; next-means-one-step 0.50 with / 0.25 without. Two of
next-means-one-step's graders were also among the pilot's eight
judge-quality misses (the triage note groups them as "next-means-one-step
x2" without naming which two); their verdicts are unsettled pending the
Sonnet re-run.

## D8 — Never advance past a wrong answer

**Decision.** Never advance past a check the learner got wrong; re-teach
from a new angle. A right conclusion reached with shaky reasoning gets the
gap named and a re-check, not a pass.

**Rejected.** Repeating the step louder; accepting a right answer for the
wrong reason.

**Cost.** A confused reader spends longer on step 2 — which is the point:
the misunderstanding surfaces at step 2, not step 6.

**Pinned by.** evals/wrong-answer-reteaches/,
evals/shaky-reasoning-rechecks/. 1-run Haiku pilot: wrong-answer-reteaches
0.50 with / 0.25 without; shaky-reasoning-rechecks 0.50 with / 0.25
without. Two grader-level notes from triage:
`wrong-answer-reteaches/does-not-affirm-the-wrong-answer` failed
identically in both arms — it was keyword-brittle on the literal word
"exactly," testing the model's vocabulary rather than the skill's
behaviour — and was rewritten in commit `7aa7414`.
`wrong-answer-reteaches/issues-a-fresh-check` and
`shaky-reasoning-rechecks/rechecks-before-moving-on` were among the
pilot's eight judge-quality misses and were left alone; their verdicts are
unsettled pending the Sonnet re-run.

## D9 — The close is the chain, then the one thing that bites

**Decision.** The close gives the whole chain back in about five lines,
one per step, then names the one thing most likely to bite them in
practice.

**Rejected.** A summary of topics covered — a table of contents after the
fact, not a chain.

**Cost.** Writing it well means having actually taught a chain rather than
a pile of facts.

**Pinned by.** evals/closing/. 1-run Haiku pilot: 0.80 with / 0.40 without
— the largest delta in the pilot. One genuine finding here, not a judge
problem: `recap-is-about-five-lines` passed (the five-line chain was
compliant), but the "thing most likely to bite them" note ran to about
four paragraphs of fresh teaching rather than a single named thing. The
author has accepted this as a refinement item (see Open); `SKILL.md` was
not changed for it.

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
one's 1-run Haiku pilot score, and the judge-quality caveats that go with
it, are given under its own Part 1 entry (D4–D9); read those before
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
rules edited to pass. Evidence for opening and the first two trigger cases
is the 1-run Haiku pilot; evals/no-trigger-explain-and-do/ ran separately,
3 runs on a Sonnet judge, after the pilot — see B6. That run found the one
red this lexical-only port has produced: the description over-triggers on
a task request that borrows its own vocabulary.

## B6 — The trigger excludes task requests

**Decision.** The skill's trigger is narrow: a request to perform a task
does not fire the skill, even when it carries an "I don't get this,
explain as you go" rider.

**Rejected.** Leaving the description broad and letting the skill fire on
"how do I add an index to this table?"

**Cost.** A genuine "explain this to me" phrased as a task request may now
go unanswered by the skill.

**Pinned by.** evals/no-trigger-task-ask/,
evals/no-trigger-mid-implementation/, evals/no-trigger-explain-and-do/.
This is a ruling with red evidence and no green evidence yet — half the
proof, not the whole of it.

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
seconds. The result is the red the spec predicted and the pilot couldn't
produce — the trigger, as currently worded, is too broad:

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

**What is not yet true:** the `description` has not been narrowed. This is
the "red before the decision" half of the evidence only. The green-after
half — a narrowed trigger re-run against `no-trigger-*` showing the same
prompt no longer firing the skill — does not exist yet. Do not read this
entry as claiming the fix already works; it claims the problem is real and
now measured.

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

**Pinned by.** Every `llm` grader in the suite. The pilot itself is the
evidence for this decision: of its reds, eight were judge-quality misses —
a small judge missing behaviour that triage confirmed was actually correct
— against two rubrics that were genuinely testing the model rather than
the plugin, and one rubric that was genuinely too literal. A judge that
misses correct behaviour nearly as often as it catches real problems is
not a judge to trust for the run whose verdict decides anything; that is
why `--judge-model sonnet` is reserved for the run that counts.

---

## Open

| Item | Open because | Resolved by |
|---|---|---|
| A ninth eval case for "read the code before step 1" (B7) | Needs a committed fixture repo and `context.add_dirs`; deliberately deferred | A later pass, if a run suggests the rule drifts |
| Part 1 of this log | The rationale is reconstructed, not authored | The author's review pass |
| Closing-step brevity: the "what will bite you" note | In the pilot, `closing`'s recap was compliant but the gotcha note ran to about four paragraphs of fresh teaching, on a 1-run Haiku pilot | A refinement pass the author has already accepted ("we'll make the closing more brief") |
| The full 3-run suite with `--judge-model sonnet` | Not yet run; the pilot was 1 run per case on a Haiku judge, thinner evidence than the suite is meant to ship on | The run that counts — settles per-case pass/fail with real confidence and re-scores the eight cases whose pilot verdict was a judge-quality miss |
| Narrowing the `description` to fix the over-triggering B6 found | `evals/no-trigger-explain-and-do/` (3 runs, Sonnet judge) showed the trigger fires on a task request that borrows its own vocabulary, Δ −1.00; the description has not been edited in response yet | Narrowing the `description`, then re-running `--case 'no-trigger-*'` to get the green-after evidence B6 is still missing |
| The B2 resumed-session hand-check | Planned as a one-off comparison against a genuinely resumed session; not yet performed | Running it and recording the verdict in B2 |
| Two installed copies of the skill | `~/.claude/skills/what-the-heck/` and the installed plugin both define `what-the-heck` on the same machine | Deleting the personal copy once the plugin is installed and verified, so this repo is the single source. The author's call |
