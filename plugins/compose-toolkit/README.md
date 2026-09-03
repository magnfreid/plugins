# compose-toolkit

**A seeding library, not a runtime authority.** Its job is to write good Android and Compose conventions into
*your project*, then get out of the way.

## Use it

```
/compose-toolkit:init-conventions
```

That writes the project's **decisions** — which libraries, which structure, which rules — into its
own `CLAUDE.md`. After that the project owns the text; edit it there.

It also copies `architecture-notes.md` into `.claude/reference/` — the reasoning behind the
structural decisions it just seeded.

## You will mostly not run it

`init-conventions` is a blank-page tool, not a prerequisite. A project that already states its
rules is already in the state it produces, and `dev-workflow:feature` reads them as they are —
whatever file they live in. Nothing here requires a layout, and nothing will ask you to reorganize
a project to match one.

The one thing it does that copying a template by hand cannot: **resolve rules that are conditional
on the project's own configuration.** The SwiftUI `@MainActor` rule is the worked example — it is
the opposite of itself depending on `SWIFT_DEFAULT_ACTOR_ISOLATION`, and the documented way that
went wrong was a human copying it and dropping the conditional. If nothing in a stack's block is
conditional, the command is doing nothing a copy-paste would not.

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

## The two halves, and why only one of them seeds

| | Lives in | Because |
|---|---|---|
| **Decisions** — which library, which structure, which APIs are banned | the project's `CLAUDE.md` | If it doesn't load, something silently goes wrong. A rule that applies 40% of the time is worse than useless |
| **Techniques** — how to write it once the decision is made | skills here | If it doesn't load, you get competent generic code instead of this specific shape. Degraded, not wrong |

That asymmetry is the whole design. It is also why the skills here carry **no decisions**: nothing
about whether to use a library, where its files live, or what things are called. Strip those out
and there is nothing left for a project's `CLAUDE.md` to contradict, so the two cannot drift.

Every drift case that motivated this — a skill asserting iOS 26 against a project on 18, dark mode
against a light-only app, Retrofit against Firebase Data Connect — was a *decision* wearing a
technique's clothes. None was a technique.

The test for anything added here: *if this doesn't load, does something silently go wrong?* If yes,
it is a decision and belongs in the seeded block, not in a skill.

## What's in here

| Piece | Role |
|---|---|
| `commands/init-conventions` | Seeds the project. The main entry point |
| `templates/claude-md-block.md` | The rules that go in `CLAUDE.md`, with placeholders read from the project |
| `templates/reference/architecture-notes.md` | The reasoning behind the seeded structure, copied into the project |

The seeder reads `.github/workflows/*.yml` before writing the verification chain, because CI is the
most reliable statement of what "passing" means, and it includes a lint task only if the project
actually configures one. It does **not** assert a networking stack or a persistence choice — that
is exactly how a toolkit ends up prescribing Retrofit to a project built on something else.
