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
/plugin install flutter-toolkit@magnus-plugins
```

## Plugins

| Plugin | Description |
| --- | --- |
| [dev-workflow](./plugins/dev-workflow) | The feature loop — plan with Opus, approve once, implement, review independently, fix, ship a PR. Stack-agnostic. |
| [flutter-toolkit](./plugins/flutter-toolkit) | Tool-specific Flutter skills — BLoC, Dio, go_router, gen-l10n, theming, testing. |

## Why there is no native toolkit

There was one for SwiftUI and one for Compose. Both were deleted, because they documented the
conventional way to use those frameworks — which is what a model does by default. A skill earns its
place by encoding a *preference that differs from convention*. Flutter's does; the native ones did
not, and 568 lines of restating Apple's and Google's guidance is a liability, not an asset.

The handful of things that genuinely surprise — OSLog interpolation being public for numbers,
Nav3 needing `rememberViewModelStoreNavEntryDecorator()` — are lines in a project's `CLAUDE.md`,
not a plugin.

## How the two plugins differ

`dev-workflow` is a **procedure** — multi-step, order matters, and a failure is visible. That is
what a skill is good at.

`flutter-toolkit` is **tool-specific technique**. How to write a BLoC, how to order Dio
interceptors, how a `ThemeExtension` gets added. It auto-triggers while you work, including inside
agents `dev-workflow:feature` spawns.

It contains **no decisions** — nothing about whether to use a library, where files live, or what
things are called. Those belong in the project's own `CLAUDE.md`, which is the project owner's
responsibility and not something these plugins write.

That split is the design:

| | Lives in | Because |
|---|---|---|
| **Decisions** — "use Dio for HTTP", "@Observable over ObservableObject", the folder tree | the project's `CLAUDE.md`, written by its owner | If it doesn't load, something silently goes wrong. A rule that applies 40% of the time is worse than useless |
| **Techniques** — how to write it once that is decided | skills in `flutter-toolkit` | If it doesn't load, you get competent generic code instead of this specific shape. Degraded, not wrong |

The test for which side a new thing belongs on: *if this doesn't load, does something silently go
wrong?* If yes, it is a decision, and it is not a skill.

## Repo layout

```
.claude-plugin/
  marketplace.json         # marketplace manifest
plugins/
  <plugin-name>/
    .claude-plugin/
      plugin.json          # plugin manifest
    skills/<skill>/SKILL.md      # procedures, and tool-specific technique
    agents/<agent>.md            # subagents the workflow spawns
```

## Versioning

Each plugin uses semver independently. `0.x.y` means "in development, expect breaking changes." Plugins graduate to `1.0.0` when their shape is stable.

## License

MIT — see [LICENSE](./LICENSE).
