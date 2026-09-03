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
| `*.xcodeproj`, `*.xcworkspace`, `Package.swift` | `swiftui` | `xcodebuild -scheme <scheme> build` → `xcodebuild test -scheme <scheme> -destination 'platform=iOS Simulator,name=iPhone 16'` |
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

If the repo has a script that already does all of this — `scripts/verify.sh`, a Makefile target,
a CI job — run that instead and skip this list. See the first rule below.

## Android verification

In order, always through the wrapper — **`./gradlew`, never a system `gradle`**:

1. `./gradlew spotlessCheck` / `ktlintCheck` / `detekt` — only if the project configures one.
2. `./gradlew assembleDebug`
3. `./gradlew lint` — Android Lint. New warnings introduced by the change count as failures.
4. `./gradlew testDebugUnitTest`
5. `./gradlew connectedDebugAndroidTest` — **only if a device or emulator is attached.**

**Step 5 needs a device and step 4 does not.** `testDebugUnitTest` runs on the JVM and will happily
report green having never touched an emulator, so a run that stops at step 4 has not exercised any
Compose UI test. Check `adb devices` first; if nothing is attached, run steps 1–4 and *say in the
report that instrumented tests were not run*. Do not silently skip them, and do not claim the suite
passed.

Gradle builds are slow, especially the first run in a session or after a dependency change. A long
run is not a hang — do not kill it and retry with a narrower task.

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
  name. If no simulator destination is available, run the build only and say in the report that
  tests were not run — do not silently skip them.
- **Unknown stack:** do not invent commands. Ask the user how the project is built and tested,
  then record the answer in `state.json` under `verification` so later steps and resumes reuse it.
