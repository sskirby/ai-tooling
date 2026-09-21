# ai-tooling

A Claude Code plugin marketplace. One plugin so far.

## Install

```
/plugin marketplace add sskirby/ai-tooling
/plugin install what-the-heck
```

### Updating, and why it needs three commands

`claude plugin install` **copies** the plugin into
`~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`. That copy is a
snapshot, not a link: a marketplace pointing at a local path does not track
your working tree, and `claude plugin marketplace update` refreshes the
marketplace without touching an already-installed plugin. So:

```
claude plugin marketplace update ai-tooling
claude plugin uninstall what-the-heck@ai-tooling
claude plugin install what-the-heck@ai-tooling
```

This matters most when developing the plugin. Edit `SKILL.md`, reinstall, or
you are testing the old copy — including when a frontmatter `description`
change is what you meant to test, since that is the only part loaded before
the skill fires.

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
