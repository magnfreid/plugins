# Stack detection

Detect from repo markers, nearest to the working directory first. Record the result in
`state.json` as `stack`. If markers for more than one stack are present (a monorepo), detect per
the path the change targets, and say which you chose in the plan's Objective.

**Conventions always come from the project**, in whatever shape it keeps them — a `CLAUDE.md` at
any level, the docs it points at, or the patterns already in the code. For every stack in this
table. There is no per-stack conventions source to look up and no plugin that outranks the repo.
What varies by stack is only how you verify.

| Marker | Stack | Verification, in order |
|---|---|---|
| `pubspec.yaml` | `flutter` | See **Flutter verification** below — the one-line version is wrong in two ways |
| `pubspec.yaml`, no `flutter:` key | `dart` | `dart analyze` → `dart format --set-exit-if-changed .` → `dart test` |
| `*.xcodeproj`, `*.xcworkspace`, `Package.swift` | `swiftui` | See **Xcode verification** below |
| `package.json` with `react-native` | `react-native` | `npx tsc --noEmit` → lint → `npm test` |
| `package.json` | `node` / `web` | `npx tsc --noEmit` (if TS) → lint → `npm test` |
| `build.gradle(.kts)` with Compose | `compose` | See **Android verification** below |
| `go.mod` | `go` | `go vet ./...` → `go test ./...` |
| `Cargo.toml` | `rust` | `cargo clippy` → `cargo test` |
| `pyproject.toml` / `requirements.txt` | `python` | lint → `pytest` |

**The project's own chain wins over this table.** Read `.github/workflows/*.yml` first — CI is the
most reliable statement of what "passing" means here — and prefer a `scripts/verify.sh` or a
Makefile target if one exists. One command that cannot drift beats four that can.

**Any claim about warnings requires a from-scratch build.** An incremental build reports nothing
for a file it did not recompile. Incremental is fine for "tests pass"; record which kind you ran.

## The fast loop and the slow suite

Every stack's verification splits in two. **The fast loop** runs on every round — after the
implement step, in the reviewer's own check, after the fix round, and after every revision: build,
analyze, format, lint, **compile every test target, the slow ones included**, and run the fast
tests. **The slow suite** — UI, integration, and instrumented tests, anything that drives a
simulator, an emulator, or a device — is compiled every round and run once, in the final run, when
Magnus says the change has settled.

Compiling it every round is the half that cannot be dropped. A UI test that stopped building fails
nothing in a loop that never compiles it, and it surfaces at the final run as a pile of breakage
from rounds nobody can tell apart any more.

| Stack | Slow suite | Compiled in the fast loop by | Run in the final run by |
|---|---|---|---|
| `swiftui` | XCUITest targets | `xcodebuild build-for-testing` | `xcodebuild test` — see **Xcode verification** |
| `flutter` | `integration_test/` | `flutter analyze` | `flutter test integration_test` — see **Flutter verification** |
| `compose` | instrumented tests | `./gradlew assembleDebugAndroidTest` | `./gradlew connectedDebugAndroidTest` — see **Android verification** |
| anything else | none, unless the repo defines one | the repo's build | the repo's command |

**The repo decides what is slow.** A CI job, script, or package script named for e2e, UI, or
integration tests — `test:e2e`, a Playwright or Cypress config, a `ui-tests` job — is the slow
suite, whatever the stack. The same rule applies to it: keep it out of the fast loop, run it in the
final run, and make sure the fast loop still builds or type-checks it.

**The project's chain still wins, with one adjustment.** If the repo's one command —
`scripts/verify.sh`, a Makefile target, the CI job — runs the slow suite too, that command is the
final run, and the fast loop is this file's per-stack fast loop. Record both.

Record the fast loop in `state.json` as `verification` and the slow suite as `slowSuite`, with the
shape in the workflow's `references/workflow-state.md`. A stack with no slow suite has no
`slowSuite`, and its final run is `verification` on the current HEAD.

## Flutter verification

In order. Two of these steps are routinely left out, and each has shipped a red CI run:

1. `fvm dart run build_runner build --delete-conflicting-outputs` — only if a Freezed or
   json_serializable file changed.
2. `fvm flutter analyze`
3. `fvm dart format --set-exit-if-changed lib packages test`
4. `fvm flutter test` — from the repo root.
5. `fvm flutter test` **inside every `packages/<member>/` that has a `test/` directory.**

**Step 5 is not optional and not a nicety.** `flutter test` from the root does not descend into
workspace members. In a repo that keeps its domain logic in `packages/` — which is the layout
the project's conventions prescribe — a root-only run silently skips most of the suite and
still prints a green summary. The failure mode is not a missing check; it is a *convincing* one.

```bash
fvm flutter test
for pkg in packages/*/; do
  [ -d "$pkg/test" ] && (cd "$pkg" && fvm flutter test) || true
done
```

**Step 3 is not optional either.** The formatter check is a hard CI failure in these repos and has
failed a PR at least once. Scope it to `lib packages test` rather than `.` so generated output
outside those trees is not dragged in.

**Integration tests are the slow suite.** `fvm flutter test` reads `test/` and never touches
`integration_test/`, so steps 4 and 5 already leave them out. Step 2 already compiles them, since
`flutter analyze` covers the whole project. The final run adds:

6. `fvm flutter test integration_test` — from the repo root, and inside every `packages/<member>/`
   that has an `integration_test/` directory. **Only on a mobile target.** Pick an iOS simulator or an
   Android emulator or device id from `fvm flutter devices`, never macOS, Chrome, or web, and pass
   `-d <id>`. With none, say in the report that integration tests were not run.

If the repo drives them some other way — `flutter drive`, a script, a CI job — use that.

If the repo has a script that already does all of this — `scripts/verify.sh`, a Makefile target,
a CI job — run that instead and skip this list. See the first rule below.

## Android verification

In order, always through the wrapper — **`./gradlew`, never a system `gradle`**:

1. `./gradlew spotlessCheck` / `ktlintCheck` / `detekt` — only if the project configures one.
2. `./gradlew assembleDebug`
3. `./gradlew lint` — Android Lint. New warnings introduced by the change count as failures.
4. `./gradlew testDebugUnitTest`
5. `./gradlew assembleDebugAndroidTest` — compiles the instrumented tests without running them.

That is the fast loop. The final run adds:

6. `./gradlew connectedDebugAndroidTest` — **only if a device or emulator is attached.**

**Step 6 needs a device and step 4 does not.** `testDebugUnitTest` runs on the JVM and will happily
report green having never touched an emulator, so the fast loop has not exercised any Compose UI
test. Step 5 is the only thing in it that notices an instrumented test that no longer compiles. At
the final run, check `adb devices` first. If nothing is attached, the final run cannot pass: *say in
the report that instrumented tests were not run*, do not claim the suite passed, and do not treat
the change as settled.

Gradle builds are slow, especially the first run in a session or after a dependency change. A long
run is not a hang — do not kill it and retry with a narrower task.

## Xcode verification

Discover the scheme with `xcodebuild -list`. Find the UI test targets in the project, not by their
names: every target whose `productType` is `"com.apple.product-type.bundle.ui-testing"` in
`project.pbxproj`. A name ending in `UITests` is a habit, not a guarantee. If the scheme uses a test
plan, read the `.xctestplan` too, because the targets it lists are the ones that run. A Swift package
with no Xcode project has no UI test targets, so it has no slow suite.

The fast loop, with `<sim>` as `platform=iOS Simulator,name=iPhone 16` unless the project or CI
names another:

1. `xcodebuild build-for-testing -scheme <scheme> -destination '<sim>'` — builds the app and
   **every** test target in the scheme, the UI tests included.
2. `xcodebuild test-without-building -scheme <scheme> -destination '<sim>' -skip-testing:<UITestTarget>`
   — one `-skip-testing:` per UI test target. Runs the unit tests against the build from step 1.

The final run adds:

3. `xcodebuild test -scheme <scheme> -destination '<sim>'` — everything, UI tests included.

Step 1 replaces a plain `build`. It compiles the same app with the test targets on top, and a plain
`build` never compiles a test target. A UI test that stopped building would survive every round
until the final one.

## Rules

- **The repo's own scripts win.** If `package.json` defines `test` and `lint`, or the Makefile has
  a `check` target, or CI runs a specific command, use that instead of the table. The table is a
  fallback for repos that have no stated convention.
- **Read CI.** `.github/workflows/*.yml` is the most reliable statement of what "passing" means in
  this repo. Prefer it over everything above.
- **FVM:** if `.fvmrc` or `.fvm/` exists, every Dart and Flutter command is prefixed `fvm`. Never
  mix `fvm flutter` and bare `flutter` in one run.
- **Gradle:** always `./gradlew`, never a system `gradle` — the wrapper pins the version the repo
  expects. Every dependency version belongs in `gradle/libs.versions.toml`.
- **Xcode:** discover the scheme with `xcodebuild -list` rather than guessing it from the folder
  name. If no simulator destination is available, run `build-for-testing` only and say in the report
  that tests were not run — do not silently skip them, and do not treat the change as settled.
- **Unknown stack:** do not invent commands. Ask the user how the project is built and tested,
  then record the answer in `state.json` under `verification` so later steps and resumes reuse it.
