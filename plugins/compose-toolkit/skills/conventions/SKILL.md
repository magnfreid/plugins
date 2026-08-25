---
name: conventions
description: The default architectural conventions for Magnus's Android and Jetpack Compose projects — MVVM with a single StateFlow UI state, Navigation 3, Hilt, a capability-grouped data layer, Material 3 tokens, and the verification chain. Load before planning or implementing any Android, Kotlin, or Compose change so defaults are applied without being restated, and whenever asked what the Android or Compose conventions are. This is the "which choice do we make" skill; it is not a setup guide.
---

# Android / Jetpack Compose conventions

These are **defaults, not laws**. They apply unless overridden. Precedence, highest first:

1. An explicit instruction from Magnus in the current session.
2. The project's `CLAUDE.md` or `.claude/conventions/compose.md`.
3. Existing patterns in the repo — if the codebase consistently does something else, mirror it and
   say so rather than converting the codebase mid-feature.
4. This file.

Departing from a default is fine. Departing silently is not: record it in the plan's
**Conventions applied** table with the reason.

Where Google states a recommendation, this file follows it. Where Google states nothing — project
structure, error mapping, what must be tested — this file decides. Both kinds are marked below.

## State

**MVVM as Google defines it.** Not MVI.

- One `uiState` per screen, exposed as an immutable `StateFlow` from an AAC `ViewModel`.
- Build it with `stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), <Initial>)` when it
  derives from a stream; `MutableStateFlow` exposed as `StateFlow` when it does not.
- Collect it with **`collectAsStateWithLifecycle()`**. Never bare `collectAsState()`.
- **User actions arrive as plain public functions** on the ViewModel — `onRefresh()`,
  `onQueryChange(query)`. Do not introduce a sealed `Action`/`Intent` union. That is the Flutter
  BLoC shape; on Android it adds ceremony the tooling does not reward.
- `XUiState` is a **data class by default**. Use a sealed interface only when the states are
  genuinely mutually exclusive (`Loading` / `Success` / `Empty` / `Error` with no shared fields).
  "The screen has a loading spinner" is not exclusivity; a nullable field covers that.

**No one-off events from the ViewModel to the UI.** No `Channel`, no `SharedFlow`, no
`SingleLiveEvent` for snackbars, toasts, or navigation. Model the outcome as state and let the UI
report consumption:

```kotlin
data class LoginUiState(
    val isSubmitting: Boolean = false,
    val errorMessage: Int? = null,   // string resource id
    val loggedIn: Boolean = false,
)
// ...and an onErrorShown() / onNavigated() function that clears it.
```

This is Google's stated recommendation and it is the most-violated rule in real Android code. If a
case genuinely cannot be expressed as state, say so explicitly in the plan and name why — do not
reach for a `Channel` quietly.

### ViewModel rules

- Never hold a reference to an `Activity`, `Context`, `View`, or `Resources`. Never
  `AndroidViewModel`.
- Emit **string resource ids**, not resolved strings — resolving requires a `Context` and breaks
  configuration changes.
- ViewModels are **screen-level only**. A reusable component with internal complexity gets a plain
  state holder class remembered in the composition, not a ViewModel.
- Talk to the data layer with `suspend` functions and `Flow`. Launch from `viewModelScope`.

## Project layout

Single module. Everything under `src/main/kotlin/com/<domain>/<app>/` — `kotlin/`, not the legacy
`java/` source dir.

```
navigation/           NavKeys.kt, Navigator.kt, AppNavDisplay.kt
di/                   Hilt modules
feature/<name>/       <Name>Screen.kt, <Name>ViewModel.kt, <Name>UiState.kt, components/
data/<capability>/    XRepository.kt, DefaultXRepository.kt, FakeXRepository.kt,
                      the domain model, XMappers.kt, source/{local,network}/
data/database/        AppDatabase.kt
designsystem/         theme/, component/, icon/
ui/                   shared composables that DO know the domain
common/               AppDispatchers.kt, Logger.kt, AppResult.kt
res/values/           strings.xml + strings_<feature>.xml
```

**`data/` is grouped by capability, not by role.** `data/auth/` owns its interface, its `Default*`
and `Fake*`, its domain model, its mappers, and its `source/{local,network}/`. Do not create a
top-level `model/` or `repository/` package.

That role-based split exists in Now in Android because NiA is **multi-module** — `core:model` is a
separate Gradle module precisely so every other module can depend on it without a cycle. That
constraint does not exist here. Google's single-module sample (`android/architecture-samples`) puts
`Task.kt`, `TaskRepository.kt`, `DefaultTaskRepository.kt`, `FakeTaskRepository.kt` and
`source/{local,network}/` together, and so do we.

**`designsystem/` versus `ui/`:** `AppButton` knows nothing about your domain; `ProductCard` does.
Keeping them apart is what lets `designsystem/` be lifted out or reused. Do not collapse them.

**`AppDatabase.kt` is the exception to capability grouping** — Room requires a single `@Database`
listing every entity. That is a framework constraint. Do not "fix" it.

## Feature structure

**`<Name>Screen.kt` holds two overloads of the same name**, plus previews:

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
) {
    // actual UI here
}
```

The stateless overload is the seam: it is what `@Preview` renders and what a Compose test drives.
This is the same split as Flutter's page/`View` rule and it exists for the same reason.

**Extraction.** Move a composable into `components/` as soon as it is *semantically distinct* — a
self-contained piece of UI with its own internal structure. Keep a `private` composable in the
screen file only for small helpers; past roughly 40–50 lines or more than a couple of parameters,
promote it. The target is a screen file that reads like a layout outline.

A second file in a feature folder is for a second genuinely distinct top-level screen. Two screens
do not earn `list/` and `detail/` subfolders; sub-flows do.

**Features own screens, not routes.** All `NavKey`s live in `navigation/NavKeys.kt`.

## Data layer

- **Depend on an interface, never a concrete implementation.** `AuthRepository` is the interface;
  `DefaultAuthRepository` is the implementation, named for its role, or for its backing technology
  when that is the point (`OfflineFirstProductRepository`).
- **Every repository ships a `FakeXRepository` in the same package, in `main/`** — not in `test/`.
  It is for previews and for UI work that should not need a network. It must never be bound in a
  production Hilt module; R8 strips it when nothing in the release graph references it.
- **No framework type crosses a repository boundary.** No `Response`, `HttpException`, Room
  `Entity`, `Cursor`, or DTO in a public repository signature. Map at the edge.
- **Failures cross as domain failures**, via `AppResult` in `common/`. A ViewModel never catches an
  `IOException` or an `HttpException`.
- **A model per layer** where they differ: `ProductDto` (wire), `ProductEntity` (Room), `Product`
  (domain). Mappers live in the capability package. If all three would be identical field-for-field
  and the wire format is stable, one class is fine — say so rather than generating ceremony.
- Repositories expose `Flow` for streams and `suspend` for one-shot actions. Naming: `getXStream()`
  for a `Flow`, verb phrases for actions.

## Navigation

**Navigation 3.** Stable since November 2025 and Google's recommendation for new apps.

- Routes are typed: `@Serializable data object ShopNavKey : NavKey`, with arguments as constructor
  properties. Never strings.
- The back stack is owned by a `Navigator` in `navigation/`, injected — never prop-drilled and never
  a singleton object.
- `NavDisplay` **must** be given `entryDecorators` including
  `rememberSaveableStateHolderNavEntryDecorator()` and `rememberViewModelStoreNavEntryDecorator()`.
  Without the latter, ViewModels are not scoped to their entry. This is the single most common Nav3
  mistake.
- Single activity. No `Fragment`, no `NavHostFragment` in new code.

**Mechanics, recipes, and nav2 migration are `android-skills:navigation-3`.** Invoke it rather than
reconstructing the API from memory — this file states the choice, that skill states the API.

## Dependency injection

- **Hilt**, with KSP. Constructor injection everywhere it is possible.
- `@HiltViewModel` for ViewModels; `hiltViewModel()` at the screen's stateful overload.
- Interfaces are bound to implementations with `@Binds` in `di/RepositoryModule.kt`. That module is
  the only place a concrete implementation is named.
- Scope only what needs it — shared mutable state or an expensive-to-build type.
- Inject dispatchers with a qualifier from `common/AppDispatchers.kt`. Never hardcode
  `Dispatchers.IO` inside a repository; it cannot be replaced in a test.

## Networking

- **Retrofit + OkHttp + kotlinx.serialization.** Not Moshi, not Gson, not Ktor — Ktor is the KMP
  choice and these projects are Android-only.
- The API interface and its DTOs live in the capability's `source/network/`. DTOs are
  `@Serializable`, annotated with `@SerialName` where the wire name differs, and never leave the
  data layer.
- Auth headers, logging, and retries belong in OkHttp interceptors, not in call sites.

## Persistence

- **Room** for structured local data; **DataStore** (Preferences, or Proto where the shape is
  non-trivial) for settings and tokens. Never `SharedPreferences` in new code.
- DAOs return `Flow` for anything the UI observes.
- Every schema change ships a migration. `fallbackToDestructiveMigration()` is not acceptable in a
  released app; if the app is pre-release and you use it, say so in the plan.

## Design system

- **Material 3, stable.** As of August 2026 that is `androidx.compose.material3:material3:1.4.0`.
  The Expressive APIs — `materialExpressiveTheme`, `WavyProgressIndicator`, the flexible app bars —
  are still `1.5.0-alphaXX`. Do not pull an alpha in without raising it first.
- Colour, typography and shape come from `MaterialTheme`. **Spacing comes from a
  `CompositionLocal`** in `designsystem/theme/Spacing.kt`, because M3 ships no spacing scale.
- No literal `Color(0xFF...)`, no `TextStyle(fontSize = 17.sp)`, no bare `Modifier.padding(13.dp)`
  in feature code. If a token is missing, add it — that is part of the work, not a follow-up.
- **In Compose you wrap.** Compose has no style protocol, so a project component
  (`designsystem/component/AppButton.kt`) is the conventional answer, not a fallback. Keep wrappers
  presentation-only and preserve the underlying component's semantics and accessibility.

## Localization

- Every user-facing string comes from `stringResource(R.string.…)`. No hardcoded literals in a
  composable, ever, including `contentDescription`.
- Feature strings live in `res/values/strings_<feature>.xml`; genuinely shared ones in
  `strings.xml`. All resolve into one `R.string` namespace.
- Quantities use `pluralStringResource`, not an `if (count == 1)`.
- A `UiState` carries `@StringRes` ids, not resolved text.

## Concurrency

- Coroutines and `Flow` throughout. `viewModelScope` in ViewModels; injected dispatchers in the data
  layer.
- No `GlobalScope`. No `runBlocking` outside tests. No callbacks or `LiveData` in new code.
- Compose side effects use the right tool: `LaunchedEffect` with honest keys, `DisposableEffect` for
  anything needing cleanup, `rememberUpdatedState` for a lambda captured by a long-lived effect.
  Never launch work from a composable body.

## Compose correctness

- `Modifier` is the **first optional parameter**, defaulted to `Modifier`, and is applied to the
  composable's outermost layout. Never accept two modifiers.
- Hoist state. A composable that owns state a caller needs is a bug.
- Types in a `UiState` should be stable: prefer `ImmutableList` (kotlinx-collections-immutable) or
  a `@Immutable`-annotated wrapper over a bare `List` when a recomposition problem is measured.
  **Do not scatter `@Stable`/`@Immutable` speculatively** — strong skipping handles most cases.
- `derivedStateOf` only for state *derived* from other state that changes more often than the
  result. It is not a memoization tool; `remember(key)` is.
- Never read a `MutableState` inside a `remember` calculation without keying on it.

## Testing

Doctrine — what to test and why — is **`dev-workflow:testing-doctrine`**. Setup — which libraries,
harnesses, and screenshot infrastructure to install — is **`android-skills:testing-setup`**. This
section is only the Android-specific bindings.

- **JUnit4**, `kotlinx-coroutines-test` (`runTest`, an injected `StandardTestDispatcher`), and
  **Turbine** for asserting on `Flow` emissions.
- **Fakes over mocks.** Use the `Fake*` that already ships beside each repository. MockK only where
  a fake would be absurd. This is Google's stated recommendation, not a house preference.
- Required: every new ViewModel (state transitions *and* error paths), every new repository's public
  contract including its failure mapping, and pure domain logic.
- One Compose test per new screen, driving the **stateless overload** with hand-built `UiState`
  values. A test that goes through `hiltViewModel()` tests Hilt, not the screen.
- Assert against strings resolved from resources, never hardcoded English.
- **Tests ship in the same PR as the code they cover.**

## Verification

Read `.github/workflows/*.yml` first — CI is the most reliable statement of what "passing" means. If
the repo has its own script or Makefile target, run that instead of this list.

Otherwise, in order, always through the wrapper (`./gradlew`, never a system `gradle`):

1. `./gradlew spotlessCheck` or `ktlintCheck` or `detekt` — only if the project configures one.
2. `./gradlew assembleDebug`
3. `./gradlew lint` — Android Lint. New warnings introduced by the change count as failures.
4. `./gradlew testDebugUnitTest`
5. `./gradlew connectedDebugAndroidTest` — **only if a device or emulator is attached.** Check with
   `adb devices`. If none is available, run the rest and *say* in the report that instrumented tests
   were not run. Never silently skip them.

A Gradle build can be slow; a long first run is not a hang.

## Style

- One public class per file. Small private helpers may share it.
- Composables are `PascalCase` and return `Unit`. Composables that return a value are `camelCase`
  (`rememberFooState()`).
- `internal` by default for anything outside its own package's public surface. `public` is a
  decision.
- No `!!`. No platform-type leakage from Java interop without a null check.
- `val` over `var`; `lateinit` only where the initialization point can be named.
- No `println` or `android.util.Log` directly — use `common/Logger.kt`.
- ktlint's official Kotlin style; do not hand-format around it.

## Dependencies

- **Every version lives in `gradle/libs.versions.toml`.** No inline version strings in a
  `build.gradle.kts`. Compose comes in via the BOM.
- Do not add a dependency inside a feature workflow. If one is genuinely needed, stop and raise it
  with the alternative you considered. New dependencies are a decision, not an implementation
  detail.

## Growth path out of single-module

Stay single-module until there is a reason. A reason is a genuine second consumer of the code, or a
measured build-time problem — not a file count.

When it comes, in this order:

1. Extract `designsystem/`, `common/`, then `data/<capability>/` into `:core:*` modules. The package
   names were chosen so this is a move, not a redesign.
2. Split features into `:feature:<name>` modules.
3. Adopt the per-feature **`api` / `impl`** split plus a `:core:navigation` module **only** if
   features must reference each other's nav keys. Current Now in Android does this —
   `feature/foryou/api` holds only the `NavKey`; `feature/foryou/impl` holds everything else.

Do not take step 3 pre-emptively. It exists to break a dependency cycle that a single module does
not have.

## Delegate, do not duplicate

Invoke these rather than reconstructing them:

| Topic | Skill |
| --- | --- |
| Navigation 3 API, recipes, nav2 migration | `android-skills:navigation-3` |
| Test libraries, harnesses, screenshot setup | `android-skills:testing-setup` |
| AGP 9 upgrade, KSP/KAPT, BuildConfig | `android-skills:agp-9-upgrade` |
| Edge-to-edge layout | `android-skills:edge-to-edge` |
| Adaptive layouts, window size classes | `android-skills:adaptive` |
| What to test and why | `dev-workflow:testing-doctrine` |
| Verifying a design handoff | `dev-workflow:design-handoff` |
