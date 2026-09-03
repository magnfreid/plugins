---
name: testing
description: How to write Android tests — runTest with an injected TestDispatcher, Turbine for asserting on Flow emissions, fakes over mocks, Compose tests driving the stateless overload, and asserting against resolved string resources. Use when writing tests for an Android ViewModel, repository, or composable.
---

# Writing Android tests

How to write the tests, once it is settled what needs covering. What to cover and why is
`dev-workflow:testing-doctrine`.

**Technique, not choice.** This is how to work with the Android test stack once the project has
decided to use it. Whether to use it at all, where the files live, and what things are called are
the project's decisions — its `CLAUDE.md` and the patterns already in the code win over anything
here, and they win without discussion. Nothing in this file is a reason to restructure a repo.

## Coroutines

`runTest` with an **injected** `StandardTestDispatcher`, not a hardcoded one. This is the payoff
for injecting dispatchers in production code: the test controls virtual time, so a delay costs
nothing and ordering is deterministic.

`UnconfinedTestDispatcher` runs eagerly and hides ordering bugs. Reach for it only when you
specifically want that, and say why.

## Asserting on a Flow

**Turbine.** A `Flow` assertion written with `toList()` either hangs on a hot flow or races on a
cold one:

```kotlin
viewModel.uiState.test {
    assertEquals(Loading, awaitItem())
    assertEquals(Success(expected), awaitItem())
    cancelAndIgnoreRemainingEvents()
}
```

The value is that `awaitItem()` fails the test on timeout rather than blocking forever, and that
unconsumed emissions are an error — so a state you did not expect is caught rather than ignored.

## Fakes over mocks

Use the `Fake*` that ships beside each repository. A fake exercises real behaviour; a mock asserts
that a call happened, which is a weaker claim that breaks on refactoring. MockK only where a fake
would be absurd.

## Compose tests

Drive the **stateless overload** with hand-built `UiState` values. Going through `hiltViewModel()`
tests Hilt, not the screen.

**Assert against strings resolved from resources**, never hardcoded English — otherwise the suite
breaks on the first translation and passes when a `stringResource` call is removed:

```kotlin
composeTestRule.onNodeWithText(
    composeTestRule.activity.getString(R.string.settings_title)
).assertIsDisplayed()
```

## Instrumented tests

`connectedDebugAndroidTest` needs a device or emulator attached — check `adb devices`. If none is
available, run the rest and **say** instrumented tests were not run. Never silently skip them and
never report the suite as green.
