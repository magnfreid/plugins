---
name: compose-ui
description: How to write correct Jetpack Compose UI — the Modifier parameter contract, stateful/stateless screen overloads for previews and tests, side effects (LaunchedEffect keys, DisposableEffect, rememberUpdatedState), recomposition stability, and when derivedStateOf is the wrong tool. Use when writing or changing any composable.
---

# Writing Compose UI

How to write composables that recompose correctly and stay testable.

**Technique, not choice.** This is how to work with Jetpack Compose once the project has decided to
use it. Whether to use it at all, where the files live, and what things are called are the
project's decisions — its `CLAUDE.md` and the patterns already in the code win over anything here,
and they win without discussion. Nothing in this file is a reason to restructure a repo.

## The two overloads

A screen is two composables of the same name — a stateful one that obtains the ViewModel, and a
stateless one that takes the state and lambdas:

```kotlin
@Composable
fun SettingsScreen(viewModel: SettingsViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    SettingsScreen(uiState = uiState, onToggleDarkMode = viewModel::onToggleDarkMode)
}

@Composable
internal fun SettingsScreen(
    uiState: SettingsUiState,
    onToggleDarkMode: (Boolean) -> Unit,
    modifier: Modifier = Modifier,
) { /* actual UI */ }
```

The stateless overload is the seam: it is what `@Preview` renders and what a Compose test drives.
A test that goes through `hiltViewModel()` is testing Hilt, not the screen.

## The Modifier contract

`Modifier` is the **first optional parameter**, defaulted to `Modifier`, and applied to the
composable's outermost layout. Never accept two modifiers — the caller cannot tell which one wins,
and the answer changes with refactoring.

## Side effects

- `LaunchedEffect` with **honest keys**. A key of `Unit` on something that should re-run when an
  argument changes is a stale-effect bug that never throws.
- `DisposableEffect` for anything needing cleanup — listeners, receivers, subscriptions.
- `rememberUpdatedState` for a lambda captured by a long-lived effect, so the effect calls the
  current one rather than the one captured at launch.
- **Never launch work from a composable body.** A body can run many times per frame, and it is not
  a lifecycle.

## Recomposition and stability

- Prefer `ImmutableList` (kotlinx-collections-immutable) or an `@Immutable` wrapper over a bare
  `List` in a state class **when a recomposition problem is measured**. Do not scatter
  `@Stable`/`@Immutable` speculatively — strong skipping handles most cases, and the annotations
  are a promise the compiler holds you to without checking.
- `derivedStateOf` is only for state *derived* from other state that changes more often than the
  result — a scroll offset producing a boolean. It is **not a memoization tool**; `remember(key)`
  is. Using it as one costs a snapshot subscription for nothing.
- **Never read a `MutableState` inside a `remember` calculation** without keying on it. The read is
  not tracked, so the value silently goes stale.

## Extraction

Move a composable into its own file as soon as it is *semantically distinct* — a self-contained
piece of UI with internal structure. Keep a `private` composable in the screen file only for small
helpers; past roughly 40–50 lines, or more than a couple of parameters, promote it.

The target is a screen file that reads like a layout outline. If you cannot see its composition at
a glance, something wants extracting.

## Naming

Composables are `PascalCase` and return `Unit`. A composable that returns a value is `camelCase` —
`rememberFooState()`.
