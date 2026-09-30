# ai-tooling

A Claude Code plugin marketplace. One plugin so far.

## Install

```
/plugin marketplace add sskirby/ai-tooling
/plugin install what-the-heck
```

### Updating

```
claude plugin marketplace update ai-tooling
claude plugin update what-the-heck@ai-tooling
```

Then restart Claude Code. `plugin update` does not refresh the marketplace
itself, so without the first command it reports the installed version as the
latest. Auto-update is off by default for third-party marketplaces; turn it on
under `/plugin` → Marketplaces to have Claude Code do both at startup.

## Plugins

| Plugin | What it does |
|---|---|
| [`what-the-heck`](plugins/what-the-heck) | Teaches one idea at a time and refuses to advance past a check you got wrong. |

### Which model to use

Don't use Haiku. Sonnet 5 on high effort gives very good results. Opus 5.5
on medium effort gives the best.

Full `what-the-heck` suite, version 0.1.1, 6 runs per case, judged by
Opus 5.5 (details in the plugin's
[evidence note](plugins/what-the-heck/README.md#evidence-note)):

| Model (effort) | Teaching cases at 1.00 | Lowest case | Graders failing with the skill |
|---|---|---|---|
| Opus 5.5 (medium) | 7 of 7 | 1.00 | 0 of 31 |
| Sonnet 5 (high) | 5 of 7 | 0.90 | 4 of 31 |
| Haiku 4.5 | 4 of 7 | 0.21 | 9 of 31 |

Haiku 4.5's 0.21 is on shaky reasoning: it accepts a right answer given for
the wrong reason and moves on to the next step. It also fired the skill on
a task request in 1 of 6 runs.

## Developing a plugin

Load the plugin from your working tree:

```
claude --plugin-dir ./plugins/what-the-heck
```

This overrides an installed copy of the same plugin for that session. After
editing, run `/reload-plugins` to pick up the change without restarting.

Bump `version` in the plugin's `.claude-plugin/plugin.json` in every change
that should reach users. Changes under `evals/`, `replays/` or the plugin's
`README.md` need no bump. Check with `uv run plugin-version-check`.

## Evals

Each plugin carries its own eval suite. Pull requests run a free lint check
only; the suite itself is a command a human runs before merging, because a full
run costs real money on a live credential:

```
uv run replay-eval ./plugins/what-the-heck \
  --model claude-opus-5-5 --max-cost-usd 25
```

`--model` is required: the model under test, as a full model ID. The judge
is Opus 5.5 (`claude-opus-5-5`) unless you pass `--judge-model`. Other
`claude plugin eval` options pass through, except `--ablation`.

Output, abbreviated (also written to `evals/replay/delta.md`):

```
| case              | kind     | with | baseline | Δ     | runs | cost  | with-only indicators | note |
| opening           | ablation | 1.00 | 0.25     | +0.75 | 3    | $1.34 |                      |      |
| closing-replay    | replay   | 1.00 | 0.53     | +0.47 | 3    | $2.30 | no-new-step 3/3      |      |
| first-step-replay | replay   | 0.96 | 0.21     | +0.75 | 3    | $2.48 |                      |      |
```

Δ is the with-plugin score minus the no-plugin score; higher means the skill
did more. A with-only indicator is a grader that runs only on the with-plugin side,
shown as passes out of runs and left out of the score.

`claude plugin eval` alone can't give a Δ for a turn in the middle of a
lesson: its no-plugin arm resumes the same transcript, skill text included,
so both arms get taught by the skill. `replay-eval` builds a baseline
without the skill and compares against that. See
[docs/replay-evals.md](docs/replay-evals.md).

## License

MIT. See [LICENSE](LICENSE).
