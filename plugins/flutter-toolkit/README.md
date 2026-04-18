# flutter-toolkit

Claude Code plugin for Flutter development. Encodes opinionated defaults around state management, testing, and project structure so Claude produces code that matches how you'd actually ship it.

## Skills

Skills trigger automatically based on what you're working on.

| Skill | Triggers on |
| --- | --- |
| [`bloc`](./skills/bloc/SKILL.md) | BLoC/Cubit state management, Freezed states, `build_runner` workflow |
| [`l10n`](./skills/l10n/SKILL.md) | ARB files, translations, `gen-l10n` codegen, adding locales |
| [`routing`](./skills/routing/SKILL.md) | `go_router` routes, navigation, shell routes, auth redirects |
| [`testing`](./skills/testing/SKILL.md) | `bloc_test`, widget tests, `mocktail` patterns |

## Commands

Slash commands you invoke explicitly.

| Command | Purpose |
| --- | --- |
| [`/scaffold-feature`](./commands/scaffold-feature.md) | Create `lib/<feature>/{bloc,view,widgets,models}` with starter files and register the route |
| [`/new-package`](./commands/new-package.md) | Create a workspace package under `packages/<name>/` and wire it into the root pubspec |

## Agents

Subagents you can delegate to. They run in their own context window with their own model, so the main session stays clean.

| Agent | Model | Role |
| --- | --- | --- |
| [`flutter-architect`](./agents/flutter-architect.md) | Opus | Plans feature architecture and produces a file-by-file blueprint. Read-only. |
| [`flutter-implementer`](./agents/flutter-implementer.md) | Sonnet | Executes a concrete plan — writes blocs, widgets, packages. |
| [`flutter-test-writer`](./agents/flutter-test-writer.md) | Haiku | Writes `bloc_test` and widget tests against a class spec. |
| [`flutter-refactor`](./agents/flutter-refactor.md) | Haiku | Mechanical refactors — rename, extract widget, move files, format. |

Typical flow: `flutter-architect` produces a plan → `flutter-implementer` writes the code → `flutter-test-writer` adds tests. You can invoke them explicitly (`> use the flutter-architect agent to plan ...`) or let the main agent delegate automatically based on the task.

## Assumptions

This plugin assumes the project follows the conventions in the companion Flutter boilerplate:

- FVM with stable channel
- `lib/` is UI-only; domain logic lives in `packages/`
- BLoC + Freezed for state, `go_router` for navigation
- `mocktail` for test mocks

If your project diverges from these, the generated code may not fit.

## Version

`0.1.0` — early, expect changes.
