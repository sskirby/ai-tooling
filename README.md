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

## Developing a plugin

Load the plugin from your working tree:

```
claude --plugin-dir ./plugins/what-the-heck
```

This overrides an installed copy of the same plugin for that session. After
editing, run `/reload-plugins` to pick up the change without restarting.

Bump `version` in the plugin's `.claude-plugin/plugin.json` in every change
that should reach users. Claude Code detects an update only when that string
changes; a new commit with the same version leaves users on their cached copy.
The marketplace entry carries no `version`, so `plugin.json` is the one place to
change it.

## Evals

Each plugin carries its own eval suite. Pull requests run a free lint check
only; the suite itself is a command a human runs before merging, because a full
run costs real money on a live credential:

```
uv run replay-eval ./plugins/what-the-heck \
  --judge-model claude-opus-5-5 --max-cost-usd 25
```

Run the suite through `replay-eval`, not `claude plugin eval` directly. It
rebuilds the replay cases from the current `SKILL.md`, runs the suite once, and
prints one table (also written to `evals/replay/delta.md`). The headline number
is Δ: the with-plugin score minus the no-plugin score. For a replay case the
wrapper pairs it with its baseline to get Δ; see
[docs/replay-evals.md](docs/replay-evals.md). Don't pass `--ablation`, and give
the plugin as a path: either one makes replay cases run a second arm that is
taught by the skill anyway, so the wrapper refuses both.

Pass the judge as a full model ID, not an alias. Leave the flag off and the
LLM graders run on Haiku; pass `opus` or `sonnet` and the model behind the
alias changes whenever the CLI does. The model under test is pinned in each
case for the same reason, and the linter refuses a case that does not pin one.

## License

MIT. See [LICENSE](LICENSE).
