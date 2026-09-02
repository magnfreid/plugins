# magnus-plugins

A personal marketplace of Claude Code plugins, focused on mobile development workflows.

## Installing

Add this marketplace to Claude Code:

```
/plugin marketplace add https://github.com/magnfreid/plugins.git
```

Then install any plugin from it:

```
/plugin install dev-workflow@magnus-plugins
/plugin install swiftui-toolkit@magnus-plugins
```

## Plugins

| Plugin | Description |
| --- | --- |
| [dev-workflow](./plugins/dev-workflow) | The feature loop — plan with Opus, approve once, implement, review independently, fix, ship a PR. Stack-agnostic. |
| [flutter-toolkit](./plugins/flutter-toolkit) | Seeds Flutter conventions into a project's own CLAUDE.md, plus BLoC / Dio / routing / l10n blueprints. |
| [swiftui-toolkit](./plugins/swiftui-toolkit) | Seeds SwiftUI conventions into a project's own CLAUDE.md, plus API-style, design-token, and testing blueprints. |
| [compose-toolkit](./plugins/compose-toolkit) | Seeds Android and Compose conventions into a project's own CLAUDE.md, plus architecture notes. |

## How the two kinds of plugin differ

`dev-workflow` is a **procedure** — multi-step, order matters, and a failure is visible. That is
what a skill is good at.

The toolkits are **seeding libraries**. They hold rules, and a rule that must hold every time
cannot depend on a skill triggering, because nothing reports that it did not. So they write their
rules into the target project's `CLAUDE.md` and `.claude/reference/`, where they are read on every
change, and where the project can edit them.

The test for which side a new thing belongs on: *if this doesn't load, does something silently go
wrong?* If yes, it is not a skill.

## Repo layout

```
.claude-plugin/
  marketplace.json         # marketplace manifest
plugins/
  <plugin-name>/
    .claude-plugin/
      plugin.json          # plugin manifest
    skills/<skill>/SKILL.md      # procedures
    commands/<cmd>.md            # explicit entry points, incl. init-conventions
    agents/<agent>.md            # subagents the workflow spawns
    templates/                   # seed material written into a target project
      claude-md-block.md
      reference/<topic>.md
```

## Versioning

Each plugin uses semver independently. `0.x.y` means "in development, expect breaking changes." Plugins graduate to `1.0.0` when their shape is stable.

## License

MIT — see [LICENSE](./LICENSE).
