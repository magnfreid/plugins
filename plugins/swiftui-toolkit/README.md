# swiftui-toolkit

Claude Code plugin for SwiftUI development. Encodes opinionated defaults around `@Observable` state,
design tokens, navigation, and testing so Claude produces code that matches how you'd actually ship
it.

Baseline: **iOS 26+, Swift 6.2+**, strict concurrency.

## Skills

Skills trigger automatically based on what you're working on.

| Skill | Triggers on |
| --- | --- |
| [`conventions`](./skills/conventions/SKILL.md) | The architectural defaults — load before planning or implementing |
| [`api-style`](./skills/api-style/SKILL.md) | Which Swift/SwiftUI APIs to use, and which are legacy |
| [`design-tokens`](./skills/design-tokens/SKILL.md) | Colours, typography, spacing, styles, wrapper components |
| [`testing`](./skills/testing/SKILL.md) | Swift Testing, `@MainActor` rules, fakes, what must be covered |
| [`logging`](./skills/logging/SKILL.md) | `OSLog`, `Logger` categories, privacy annotations |

Cross-stack doctrine lives in `dev-workflow`: what to test and why
(`dev-workflow:testing-doctrine`), how a design handoff becomes shipped UI
(`dev-workflow:design-handoff`), and branch/commit/PR structure (`dev-workflow:pr-conventions`).

## Commands

| Command | Purpose |
| --- | --- |
| [`/new-swiftui-app`](./commands/new-swiftui-app.md) | Scaffold a new app laid out for this toolkit |
| [`/scaffold-feature`](./commands/scaffold-feature.md) | Create a feature folder and register its route |

## Agents

| Agent | Model | Role |
| --- | --- | --- |
| [`swiftui-architect`](./agents/swiftui-architect.md) | Opus | Plans feature architecture. Read-only. |
| [`swiftui-implementer`](./agents/swiftui-implementer.md) | Sonnet | Executes a concrete plan. |
| [`swiftui-test-writer`](./agents/swiftui-test-writer.md) | Haiku | Writes Swift Testing cases against a spec. |
| [`swiftui-refactor`](./agents/swiftui-refactor.md) | Haiku | Mechanical refactors. |

## Install

```
/plugin install swiftui-toolkit@magnus-plugins
```

## Version

See [`.claude-plugin/plugin.json`](./.claude-plugin/plugin.json) — currently `0.3.0`.
