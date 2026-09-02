# flutter-toolkit

**A seeding library, not a runtime authority.** Its job is to write good Flutter conventions into
*your project*, then get out of the way.

## Use it

```
/flutter-toolkit:init-conventions
```

That writes a Flutter conventions block into the project's own `CLAUDE.md` and copies the long-form
blueprints into `.claude/reference/`. After that the project owns the text — edit it there.

## Why it works this way

A skill only applies if it triggers, and triggering is a judgment call made from a `description`
against whatever you happened to type. That is fine for reference material. It is not fine for a
rule that must hold every time, and the failure is silent — nothing reports that a convention was
never consulted.

The evidence was a real session that implemented ~3,600 lines across two platforms with **zero**
skill invocations. The output was mostly fine, but only because the project's own `CLAUDE.md` files
happened to be thorough. The conventions skills never loaded.

So the rules moved to where they are always read, and this plugin became the thing that puts them
there — well-written, and **read from your actual build configuration** rather than asserted. That
second part matters: a toolkit that confidently states a default the project already decided
against is worse than no toolkit, because the wrong rule gets followed.

The test for anything added here: *if this doesn't load, does something silently go wrong?* If yes,
it belongs in the seeded block, not in a skill.

## What's in here

| Piece | Role |
|---|---|
| `commands/init-conventions` | Seeds the project. The main entry point |
| `commands/new-package` | Add a workspace package and register it |
| `commands/scaffold-feature` | Add a feature folder, bloc, view, and route |
| `templates/claude-md-block.md` | The rules that go in `CLAUDE.md`, with placeholders read from the project |
| `templates/reference/` | `bloc`, `dio`, `routing`, `l10n`, `design-tokens`, `testing` — copied in only where the project uses them |

The seeder reads the root `pubspec.yaml` to find out whether the repo uses a Dart workspace or path
dependencies, and describes the one it found rather than the one it prefers. It skips blueprints the
project has no use for — a repo with no HTTP layer should not be carrying 600 lines about Dio.
