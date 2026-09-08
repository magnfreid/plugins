# Repository conventions

A marketplace of Claude Code plugins. Each plugin lives in `plugins/<name>/`, with its manifest at
`plugins/<name>/.claude-plugin/plugin.json`.

## Version bumps are part of the change, not a follow-up

**Any change touching a file under `plugins/<name>/` bumps `version` in that plugin's
`plugin.json`, in the same PR.** This is installed from the marketplace, and `claude plugin update`
has no way to see a change that did not move the version — an unbumped change ships to nobody, and
the omission is invisible until someone notices the plugin is stale.

Skills, agents, commands, references, and the plugin README all count. Documentation-only is not an
exception: these plugins *are* documentation, so a prompt change is a behaviour change.

| Change | Bump |
|---|---|
| A new skill, agent, or command, or a change to what an existing one does | minor — `0.7.0` → `0.8.0` |
| A correction restoring behaviour that was already intended — a broken reference, a wrong path, a typo | patch — `0.7.0` → `0.7.1` |
| Removing or renaming something users invoke by name | minor while pre-1.0, and say so in the PR body |

`marketplace.json` lists plugins by source path and pins no versions, so a bump never needs it.

`scripts/check-version-bumps.sh` enforces this and runs on every PR. Run it before pushing:

```bash
./scripts/check-version-bumps.sh
```

## Where things go

Doctrine that holds across stacks lives in `dev-workflow`. Stack-specific patterns live in that
stack's toolkit. A rule that must hold every time belongs in the *target* repo's `CLAUDE.md`, not
in a skill — a skill only applies when it triggers.
