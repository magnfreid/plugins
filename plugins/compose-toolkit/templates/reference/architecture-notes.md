# Android architecture notes

The reasoning behind the structural rules in `CLAUDE.md`. Read this when a rule looks arbitrary, or
when you are about to depart from one — the reasons say what a departure costs.

## Why `data/` groups by capability, not by role

`data/auth/` owns its interface, its `Default*` and `Fake*`, its domain model, its mappers, and its
`source/{local,network}/`. There is no top-level `model/` or `repository/` package.

The role-based split — `core:model`, `core:data` — exists in Now in Android because NiA is
**multi-module**. `core:model` is a separate Gradle module precisely so every other module can
depend on it without a dependency cycle. That constraint does not exist in a single module, and
importing the layout without importing the constraint gives you the cost with none of the benefit.

Google's own single-module sample (`android/architecture-samples`) puts `Task.kt`,
`TaskRepository.kt`, `DefaultTaskRepository.kt`, `FakeTaskRepository.kt` and
`source/{local,network}/` together. So do we.

`AppDatabase.kt` is the exception, and it is a framework constraint rather than a choice: Room
requires a single `@Database` listing every entity. Do not "fix" it.

## Why `designsystem/` and `ui/` stay apart

`AppButton` knows nothing about your domain. `ProductCard` does. Keeping them in separate packages
is the entire reason `designsystem/` can be lifted out, reused, or handed to a second app. Collapse
them and that option is gone — not immediately, but by a hundred small imports.

## Why you wrap components in Compose

Compose has no style protocol. SwiftUI has `ButtonStyle`; Compose does not, so a project component
in `designsystem/component/` is the conventional answer rather than a fallback. Keep the wrapper
presentation-only, and preserve the underlying component's semantics and accessibility — a wrapper
that drops `onClickLabel` is a regression that no test will catch.

## A model per layer, when they differ

`ProductDto` (wire), `ProductEntity` (Room), `Product` (domain), with mappers in the capability
package. If all three would be identical field-for-field *and* the wire format is stable, one class
is fine — say so in the plan rather than generating ceremony to satisfy a diagram.

The rule that does not bend: no framework type in a public repository signature. A `Response`, an
`HttpException`, a `Cursor`, or a DTO crossing that boundary means every caller now depends on the
transport, and the fake cannot be written without it.

## Extraction thresholds

Move a composable into `components/` as soon as it is *semantically distinct* — a self-contained
piece of UI with its own internal structure. Keep a `private` composable in the screen file only
for small helpers; past roughly 40–50 lines, or more than a couple of parameters, promote it.

The target is a screen file that reads like a layout outline. If you cannot see the screen's
composition at a glance, something in it wants extracting.

A second file in a feature folder is for a second genuinely distinct top-level screen. Two screens
do not earn `list/` and `detail/` subfolders; sub-flows do.

## Compose correctness notes that are easy to get wrong

- **Stability.** Prefer `ImmutableList` (kotlinx-collections-immutable) or an `@Immutable` wrapper
  over a bare `List` in a `UiState` *when a recomposition problem is measured*. Do not scatter
  `@Stable`/`@Immutable` speculatively — strong skipping handles most cases, and the annotations
  are a promise the compiler will hold you to.
- **`derivedStateOf`** is only for state derived from other state that changes more often than the
  result. It is not a memoization tool; `remember(key)` is.
- **Never read a `MutableState` inside a `remember` calculation** without keying on it.
- **Side effects:** `LaunchedEffect` with honest keys, `DisposableEffect` for anything needing
  cleanup, `rememberUpdatedState` for a lambda captured by a long-lived effect. Never launch work
  from a composable body.

## Growth path out of single-module

Stay single-module until there is a reason. A reason is a genuine second consumer of the code, or a
measured build-time problem — not a file count.

When it comes, in this order:

1. Extract `designsystem/`, `common/`, then `data/<capability>/` into `:core:*` modules. The
   package names were chosen so this is a move, not a redesign.
2. Split features into `:feature:<name>` modules.
3. Adopt the per-feature **`api` / `impl`** split plus a `:core:navigation` module **only** if
   features must reference each other's nav keys. Current Now in Android does this —
   `feature/foryou/api` holds only the `NavKey`, `feature/foryou/impl` holds everything else.

Do not take step 3 pre-emptively. It exists to break a dependency cycle that a single module does
not have.

## Style rules worth keeping

- One public class per file; small private helpers may share it.
- Composables are `PascalCase` and return `Unit`. Composables that return a value are `camelCase`
  (`rememberFooState()`).
- `internal` by default outside a package's public surface. `public` is a decision.
- No `!!`. No platform-type leakage from Java interop without a null check.
- `val` over `var`; `lateinit` only where the initialization point can be named.
- No `println` or `android.util.Log` — use `common/Logger.kt`.
- ktlint's official Kotlin style; do not hand-format around it.
