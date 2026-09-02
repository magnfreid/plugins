# compose-toolkit

**A seeding library, not a runtime authority.** Its job is to write good Android and Compose conventions into
*your project*, then get out of the way.

## Use it

```
/compose-toolkit:init-conventions
```

That writes a Android and Compose conventions block into the project's own `CLAUDE.md` and copies the long-form
blueprints into `.claude/reference/`. After that the project owns the text — edit it there.

## You do not have to run it

`init-conventions` is a shortcut, not a prerequisite. If your project already states its rules —
a `CLAUDE.md` at the root, another in `android/`, another in `ios/` — then it is already in the
state this command produces, and `dev-workflow:feature` reads them as they are. Nothing in these
plugins requires a particular file layout, and nothing will ask you to reorganize a project to
match one.

Run it when a project has *not* written its rules down yet, and you want a good starting point
rather than a blank page. After that the project owns the text; re-running is never required, and
the command refuses to append a second block over one you have edited.

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
| `templates/claude-md-block.md` | The rules that go in `CLAUDE.md`, with placeholders read from the project |
| `templates/reference/` | `architecture-notes` — why `data/` groups by capability, why `designsystem/` and `ui/` stay apart, the growth path out of single-module |

The seeder reads `.github/workflows/*.yml` before writing the verification chain, because CI is the
most reliable statement of what "passing" means, and it includes a lint task only if the project
actually configures one. It does **not** assert a networking stack or a persistence choice — that
is exactly how a toolkit ends up prescribing Retrofit to a project built on something else.
