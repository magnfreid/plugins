# compose-toolkit

Tool-specific Android / Compose skills. They describe **how** to use something once your project has decided to
use it — nothing more.

## Use it

Nothing to set up. Install the plugin and the skills trigger on their own while you work, including
inside agents spawned by `dev-workflow:feature`.

"add a view model for settings" → `viewmodel-state`. "why is this recomposing" → `compose-ui`.

## What it deliberately does not do

**It does not decide anything.** Whether to use Dio, whether state is BLoC or something else,
whether `@Observable` replaces `ObservableObject`, what the folder tree looks like — those are the
project owner's calls, and they belong in the project's own `CLAUDE.md` where they are read on
every change.

That split is the whole design:

| | Lives in | Because |
|---|---|---|
| **Decisions** — which library, which structure, which APIs are banned | the project's `CLAUDE.md` | If it doesn't load, something silently goes wrong. A rule that applies 40% of the time is worse than useless |
| **Techniques** — how to write it once the decision is made | skills here | If it doesn't load, you get competent generic code instead of this specific shape. Degraded, not wrong |

Every skill here carries no decisions at all: nothing about whether to use a library, where its
files live, or what things are called. Strip those out and there is nothing left for a project's
`CLAUDE.md` to contradict, so the two cannot drift.

This was learned the hard way. Every drift case that motivated the split — a skill asserting iOS 26
against a project on 18, dark variants against a light-only app, Retrofit against a project on
Firebase Data Connect — was a *decision* wearing a technique's clothes. None was a technique.

## What's in here

| Piece | Role |
|---|---|
| `skills/viewmodel-state` | StateFlow uiState, collectAsStateWithLifecycle, outcomes as state not events |
| `skills/compose-ui` | Modifier contract, stateful/stateless overloads, side effects, stability |
| `skills/hilt` | Constructor injection, @Binds modules, scoping, injected dispatchers |
| `skills/testing` | runTest with an injected dispatcher, Turbine, fakes, Compose tests |

## Adding to it

The test: *if this doesn't load, does something silently go wrong?* If yes, it is a decision, it
belongs in a project's `CLAUDE.md`, and it must not go here.
