# ai-tooling

A Claude Code plugin marketplace. One plugin so far.

## Install

```
/plugin marketplace add sskirby/ai-tooling
/plugin install what-the-heck
```

## Plugins

| Plugin | What it does |
|---|---|
| [`what-the-heck`](plugins/what-the-heck) | Teaches one idea at a time and refuses to advance past a check you got wrong. |

## Evals

Each plugin carries its own eval suite. Pull requests run a free lint check
only; the suite itself is a command a human runs before merging, because a full
run costs real money on a live credential:

```
claude plugin eval ./plugins/what-the-heck --max-cost-usd 15
```

The headline number is Δ — the with-plugin score minus the without-plugin score.

## License

MIT. See [LICENSE](LICENSE).
