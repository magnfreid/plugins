# swiftui-toolkit

**A seeding library, not a runtime authority.** Its job is to write good SwiftUI conventions into
*your project*, then get out of the way.

## Use it

```
/swiftui-toolkit:init-conventions
```

That writes a SwiftUI conventions block into the project's own `CLAUDE.md` and copies the long-form
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
| `commands/new-swiftui-app` | Scaffold a new app, then seed it |
| `commands/scaffold-feature` | Add a feature folder, route, and strings |
| `templates/claude-md-block.md` | The rules that go in `CLAUDE.md`, with placeholders read from the project |
| `templates/reference/` | `api-style`, `design-tokens`, `logging`, `testing` — too long for `CLAUDE.md`, too specific to reconstruct |

The seeder deliberately does **not** assert a deployment target, a dark-mode policy, or whether
SwiftData is used. Those are product decisions. It reads `SWIFT_DEFAULT_ACTOR_ISOLATION` before
writing the `@MainActor` rule, because that rule is the opposite of itself depending on the setting
— and a copied rule that lost its conditional is a wrong rule in an always-loaded file.
