# magnus-plugins

A personal marketplace of Claude Code plugins, focused on mobile development workflows.

## Installing

Add this marketplace to Claude Code:

```
/plugin marketplace add github.com/magnfreid/magnus-plugins
```

Then install any plugin from it:

```
/plugin install flutter-toolkit@magnus-plugins
```

## Plugins

| Plugin | Description |
| --- | --- |
| [flutter-toolkit](./plugins/flutter-toolkit) | Flutter development workflows — BLoC state management, testing patterns, feature scaffolding. |

## Repo layout

```
.claude-plugin/
  marketplace.json         # marketplace manifest
plugins/
  <plugin-name>/
    .claude-plugin/
      plugin.json          # plugin manifest
    skills/<skill>/SKILL.md
    commands/<cmd>.md
```

## Versioning

Each plugin uses semver independently. `0.x.y` means "in development, expect breaking changes." Plugins graduate to `1.0.0` when their shape is stable.

## License

MIT — see [LICENSE](./LICENSE).
