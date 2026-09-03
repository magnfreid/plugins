---
name: viewmodel-state
description: How to shape Android ViewModel state with StateFlow — building a uiState with stateIn or MutableStateFlow, collecting it with collectAsStateWithLifecycle, modelling one-off outcomes (snackbars, navigation) as state rather than a Channel or SharedFlow, and keeping Context out of the ViewModel. Use when writing or changing a ViewModel, a UiState, or the composable that collects it.
---

# ViewModel state with StateFlow

How to shape a screen's state once it is being built with an AAC `ViewModel` and `StateFlow`.

**Technique, not choice.** This is how to work with ViewModel + StateFlow once the project has
decided to use it. Whether to use it at all, where the files live, and what things are called are
the project's decisions — its `CLAUDE.md` and the patterns already in the code win over anything
here, and they win without discussion. Nothing in this file is a reason to restructure a repo.

## Building the state

One `uiState` per screen, exposed immutably:

```kotlin
// derived from a stream
val uiState: StateFlow<SettingsUiState> =
    repository.settingsStream
        .map(::toUiState)
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), SettingsUiState.Loading)

// not derived from a stream
private val _uiState = MutableStateFlow(LoginUiState())
val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()
```

`WhileSubscribed(5_000)` is the number that matters: it keeps the upstream alive across a
configuration change without keeping it alive in the background. `Eagerly` leaks work; `Lazily`
never stops it.

## Collecting it

```kotlin
val uiState by viewModel.uiState.collectAsStateWithLifecycle()
```

**Never bare `collectAsState()`.** It keeps collecting while the app is in the background, which
turns an idle screen into a live subscription — the bug does not show up locally and does show up
on a battery report.

## Data class or sealed interface

A `data class` by default. A sealed interface only when the states are genuinely mutually exclusive
with no shared fields — `Loading` / `Success` / `Empty` / `Error`.

"The screen has a loading spinner" is not exclusivity: a `isLoading: Boolean` alongside the data is
the simpler model, and it lets the UI show stale content while refreshing, which a sealed union
makes awkward.

## One-off outcomes are state, not events

No `Channel`, no `SharedFlow`, no `SingleLiveEvent` for a snackbar, a toast, or a navigation
trigger. Model the outcome as state and let the UI report that it consumed it:

```kotlin
data class LoginUiState(
    val isSubmitting: Boolean = false,
    val errorMessage: Int? = null,   // a string resource id, not a resolved string
    val loggedIn: Boolean = false,
)

fun onErrorShown() { _uiState.update { it.copy(errorMessage = null) } }
```

This is the most-violated recommendation in real Android code, and the reason is that a `Channel`
looks like it works: it does, until a configuration change drops the event mid-flight, or a second
collector takes it. State survives both, because state is what the UI re-reads.

If a case genuinely cannot be expressed as state, say so explicitly and name why. Do not reach for
a `Channel` quietly.

## What must not be in a ViewModel

- No `Activity`, `Context`, `View`, or `Resources`. No `AndroidViewModel`.
- **Emit `@StringRes` ids, not resolved strings.** Resolving needs a `Context`, and a string
  resolved at emit time is wrong after a locale change.
- ViewModels are screen-level. A reusable component with internal complexity gets a plain state
  holder class remembered in the composition instead.
- Talk to the data layer with `suspend` functions and `Flow`, launched from `viewModelScope`.
