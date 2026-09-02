<!--
  Seed template for /compose-toolkit:init-conventions.
  {{DOUBLE_BRACES}} are placeholders the seeder MUST resolve by reading the project.
  Never emit a placeholder, and never guess one — if it cannot be read, ask.
  Once seeded, the project owns this text. Edit it there, not here.
-->

## Android / Compose conventions

Binding rules for this project. Where the codebase already does something else consistently,
the codebase wins — say so rather than converting it mid-feature.

### Structure

Single module, under `{{SOURCE_ROOT}}` — `kotlin/`, not the legacy `java/` source dir.

```
navigation/           NavKeys.kt, Navigator.kt, AppNavDisplay.kt
di/                   Hilt modules
feature/<name>/       <Name>Screen.kt, <Name>ViewModel.kt, <Name>UiState.kt, components/
data/<capability>/    XRepository.kt, DefaultXRepository.kt, FakeXRepository.kt,
                      the domain model, XMappers.kt, source/{local,network}/
designsystem/         theme/, component/, icon/   — knows nothing about the domain
ui/                   shared composables that DO know the domain
common/               AppDispatchers.kt, Logger.kt, AppResult.kt
res/values/           strings.xml + strings_<feature>.xml
```

`data/` groups by **capability, not by role** — no top-level `model/` or `repository/` package.
`AppDatabase.kt` is the one exception: Room requires a single `@Database`. The reasoning, and the
path out of single-module when it is time, is in `.claude/reference/architecture-notes.md`.

### Rules

- **MVVM, not MVI.** One `uiState` per screen, exposed as an immutable `StateFlow` from an AAC
  `ViewModel`. User actions arrive as plain public functions (`onRefresh()`, `onQueryChange(q)`) —
  no sealed `Action`/`Intent` union.
- **`collectAsStateWithLifecycle()`.** Never bare `collectAsState()`.
- **No one-off events from ViewModel to UI.** No `Channel`, no `SharedFlow`, no `SingleLiveEvent`
  for snackbars, toasts, or navigation. Model the outcome as state and have the UI report
  consumption (`onErrorShown()`). This is the most-violated rule in real Android code.
- **ViewModels hold no `Context`.** No `Activity`, `View`, `Resources`, or `AndroidViewModel`.
  Emit `@StringRes` ids, not resolved strings.
- **Screens come in two overloads of the same name** — a stateful one taking `hiltViewModel()`, and
  an `internal` stateless one taking `uiState` plus lambdas. The stateless overload is the seam
  `@Preview` renders and tests drive.
- **Navigation 3, typed `NavKey`s**, back stack owned by an injected `Navigator`. `NavDisplay` must
  be given `entryDecorators` including `rememberViewModelStoreNavEntryDecorator()` — without it,
  ViewModels are not scoped to their entry. Single activity, no `Fragment`.
- **Depend on a repository interface, never an implementation.** Every repository ships a
  `FakeXRepository` beside it in `main/`, never bound in a production Hilt module. No framework
  type (`Response`, `HttpException`, Room `Entity`, DTO) crosses a repository boundary; failures
  cross as domain failures via `AppResult`.
- **Inject dispatchers** from `common/AppDispatchers.kt`. Never hardcode `Dispatchers.IO` inside a
  repository — it cannot be replaced in a test.
- **No literal styling in feature code.** No `Color(0xFF…)`, no `TextStyle(fontSize = 17.sp)`, no
  bare `Modifier.padding(13.dp)`. Colour, type and shape come from `MaterialTheme`; spacing from
  the `CompositionLocal` in `designsystem/theme/Spacing.kt`, because M3 ships no spacing scale.
- **`Modifier` is the first optional parameter**, defaulted, applied to the outermost layout.
  Never accept two.
- **Every user-facing string is `stringResource(R.string.…)`**, including `contentDescription`.
  Quantities use `pluralStringResource`.
- **Every version lives in `gradle/libs.versions.toml`.** No inline version strings.
- **Tests ship in the same PR as the code they cover.** Required: every ViewModel (transitions
  *and* error paths), every repository contract including failure mapping, pure domain logic.
  Fakes over mocks. Turbine for `Flow` assertions. Compose tests drive the stateless overload.

### Verification

{{CI_NOTE}}Always through the wrapper — `./gradlew`, never a system `gradle`:

```
{{VERIFY_CHAIN}}
```

**A warning introduced by the change counts as a failure.** That single rule replaces a list of
banned APIs: it catches next year's deprecations too, and it cannot go stale.

`connectedDebugAndroidTest` runs **only** with a device attached — check `adb devices`. If none is,
run the rest and say instrumented tests were not run. Never silently skip them.

A Gradle build can be slow; a long first run is not a hang.

### Reference

Longer-form patterns live in `.claude/reference/`. Read the one you need rather than reconstructing
it: {{REFERENCE_LIST}}
