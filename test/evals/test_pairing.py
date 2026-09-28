import json
import tempfile
import unittest
from pathlib import Path

from evals.eval_types import EvalResult
from evals.pairing import loaded_plugins, pair_results, render_markdown, results_problems, run_score


def grader(name, passed, scored=True, with_only=False, weight=1):
    return {"name": name, "passed": passed, "weight": weight, "scored": scored, "withOnly": with_only}


def run(graders, score=None, error=None, cost=0.1, trace=None, skipped=False):
    if score is None:
        scored = [g for g in graders if g["scored"]]
        score = sum(g["weight"] for g in scored if g["passed"]) / sum(g["weight"] for g in scored)
    return {"score": score, "error": error, "costUsd": cost, "judgeCostUsd": 0.05,
            "skippedPaidGraders": skipped, "tracePath": trace, "graders": graders}


def case(name, with_runs, without_runs=None, aggregates=None):
    arms = {"with": with_runs}
    if without_runs is not None:
        arms["without"] = without_runs
    return {"name": name, "arms": arms, "aggregates": aggregates or {}}


# Replay run as the CLI scores it in a single-arm case: the with-only grader counts.
REPLAY_RUN = run([grader("keeps-route", True), grader("not-repeated", True), grader("step-heading", False)])
BASE_RUN = run([grader("keeps-route", False), grader("not-repeated", True)])
WITH_ONLY = {"lesson-replay": frozenset({"step-heading"})}


class RunScore(unittest.TestCase):
    def test_matches_cli_when_nothing_excluded(self):
        self.assertAlmostEqual(run_score(REPLAY_RUN), 2 / 3)

    def test_excluding_with_only_matches_the_cli_under_two_arms(self):
        # Under with-without the CLI itself leaves the with-only grader out of the score.
        cli_two_arm = run([grader("keeps-route", True), grader("not-repeated", True),
                           grader("step-heading", False, scored=False, with_only=True)])
        self.assertEqual(cli_two_arm["score"], 1.0)
        self.assertEqual(run_score(REPLAY_RUN, frozenset({"step-heading"})), cli_two_arm["score"])

    def test_weights(self):
        r = run([grader("a", True, weight=3), grader("b", False, weight=1)])
        self.assertEqual(run_score(r), 0.75)

    def test_errored_run_keeps_cli_score(self):
        self.assertEqual(run_score(run([], score=0, error="timeout")), 0)


class PairResults(unittest.TestCase):
    def rows(self, cases):
        return {r.case: r for r in pair_results({"cases": cases}, WITH_ONLY)}

    def test_paired_delta_and_indicator(self):
        rows = self.rows([case("lesson-replay", [REPLAY_RUN, REPLAY_RUN]),
                          case("lesson-replay-baseline", [BASE_RUN, BASE_RUN])])
        self.assertEqual(list(rows), ["lesson-replay"])
        row = rows["lesson-replay"]
        self.assertEqual((row.kind, row.score, row.baseline, row.delta), ("replay", 1.0, 0.5, 0.5))
        self.assertEqual(row.indicators, {"step-heading": "0/2"})
        self.assertEqual(row.runs, 2)
        self.assertAlmostEqual(row.cost_usd, 4 * 0.1)

    def test_native_case_uses_cli_delta(self):
        agg = {"score": 1.0, "scoreWithout": 0.25, "delta": 0.75}
        row = self.rows([case("opening", [BASE_RUN], [BASE_RUN], agg)])["opening"]
        self.assertEqual((row.kind, row.score, row.baseline, row.delta), ("ablation", 1.0, 0.25, 0.75))

    def test_missing_baseline_gives_no_delta(self):
        row = self.rows([case("lesson-replay", [REPLAY_RUN])])["lesson-replay"]
        self.assertIsNone(row.delta)
        self.assertEqual(row.note, "baseline missing")

    def test_missing_replay_case_still_gets_a_row(self):
        row = self.rows([case("lesson-replay-baseline", [BASE_RUN])])["lesson-replay"]
        self.assertEqual((row.kind, row.score, row.baseline, row.delta), ("replay", None, 0.5, None))
        self.assertEqual(row.note, "replay missing")

    def test_pair_filtered_out_gives_no_row(self):
        self.assertEqual(self.rows([]), {})

    def test_no_runs_says_so(self):
        row = self.rows([case("lesson-replay", []), case("lesson-replay-baseline", [])])["lesson-replay"]
        self.assertIsNone(row.score)
        self.assertIsNone(row.delta)
        self.assertEqual(row.note, "no runs")

    def test_errored_or_partial_runs_are_noted(self):
        rows = self.rows([case("lesson-replay", [REPLAY_RUN, run([], score=0, error="timeout")]),
                          case("lesson-replay-baseline", [run(BASE_RUN["graders"], skipped=True)])])
        self.assertIn("1 run errored", rows["lesson-replay"].note)
        self.assertIn("paid graders skipped", rows["lesson-replay"].note)

    def test_baseline_empty_side_is_noted(self):
        row = self.rows([case("lesson-replay", [REPLAY_RUN]),
                         case("lesson-replay-baseline", [])])["lesson-replay"]
        self.assertIsNone(row.delta)
        self.assertEqual(row.note, "baseline: no runs")


class ResultsProblems(unittest.TestCase):
    def test_replay_case_with_two_arms(self):
        problems = results_problems({"cases": [case("lesson-replay", [REPLAY_RUN], [REPLAY_RUN])]}, {"lesson-replay"})
        self.assertEqual(len(problems), 1)
        self.assertIn("--ablation", problems[0])

    def test_baseline_that_loaded_the_plugin(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = Path(tmp) / "trace.jsonl"
            init = {"type": "system", "subtype": "init", "plugins": [
                {"name": "replay-baseline-stub", "source": "replay-baseline-stub@inline"},
                {"name": "what-the-heck", "source": "what-the-heck@inline"},
                {"name": "agents-md", "source": "agents-md@builtin"}]}
            trace.write_text("not json\n" + json.dumps(init) + "\n")
            self.assertEqual(loaded_plugins(trace), ["replay-baseline-stub", "what-the-heck"])
            result: EvalResult = {"cases": [case("lesson-replay-baseline", [run(BASE_RUN["graders"], trace=str(trace))])]}
            problems = results_problems(result, {"lesson-replay"})
        self.assertEqual(len(problems), 1)
        self.assertIn("what-the-heck", problems[0])

    def test_clean_results(self):
        result: EvalResult = {"cases": [case("lesson-replay", [REPLAY_RUN]), case("lesson-replay-baseline", [BASE_RUN]),
                                        case("opening", [BASE_RUN], [BASE_RUN])]}
        self.assertEqual(results_problems(result, {"lesson-replay"}), [])


class Render(unittest.TestCase):
    def test_table(self):
        rows = pair_results({"cases": [case("lesson-replay", [REPLAY_RUN]), case("lesson-replay-baseline", [BASE_RUN])]},
                            WITH_ONLY)
        table = render_markdown(rows)
        self.assertIn("| lesson-replay | replay | 1.00 | 0.50 | +0.50 | 1 |", table)
        self.assertIn("step-heading 0/1", table)


if __name__ == "__main__":
    unittest.main()
