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

## Assumptions

This plugin assumes the project follows the conventions in the companion Flutter boilerplate:

- FVM with stable channel
- `lib/` is UI-only; domain logic lives in `packages/`
- BLoC + Freezed for state, `go_router` for navigation
- `mocktail` for test mocks

If your project diverges from these, the generated code may not fit.

## Version

`0.1.0` — early, expect changes.
