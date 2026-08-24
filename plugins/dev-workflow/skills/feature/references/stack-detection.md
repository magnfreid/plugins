# Stack detection

Detect from repo markers, nearest to the working directory first. Record the result in
`state.json` as `stack`. If markers for more than one stack are present (a monorepo), detect per
the path the change targets, and say which you chose in the plan's Objective.

| Marker | Stack | Conventions source | Verification, in order |
|---|---|---|---|
| `pubspec.yaml` | `flutter` | `flutter-toolkit:conventions` | `fvm dart run build_runner build --delete-conflicting-outputs` (only if Freezed/json_serializable files changed) → `fvm dart analyze` → `fvm flutter test` |
| `pubspec.yaml`, no `flutter:` key | `dart` | `flutter-toolkit:conventions` | `dart analyze` → `dart test` |
| `*.xcodeproj`, `*.xcworkspace`, `Package.swift` | `swiftui` | `swiftui-toolkit:conventions` | `xcodebuild -scheme <scheme> build` → `xcodebuild test -scheme <scheme> -destination 'platform=iOS Simulator,name=iPhone 16'` |
| `package.json` with `react-native` | `react-native` | project only | `npx tsc --noEmit` → lint → `npm test` |
| `package.json` | `node` / `web` | project only | `npx tsc --noEmit` (if TS) → lint → `npm test` |
| `build.gradle(.kts)` with Compose | `compose` | project only | `./gradlew lint` → `./gradlew test` |
| `go.mod` | `go` | project only | `go vet ./...` → `go test ./...` |
| `Cargo.toml` | `rust` | project only | `cargo clippy` → `cargo test` |
| `pyproject.toml` / `requirements.txt` | `python` | project only | lint → `pytest` |

## Rules

- **The repo's own scripts win.** If `package.json` defines `test` and `lint`, or the Makefile has
  a `check` target, or CI runs a specific command, use that instead of the table. The table is a
  fallback for repos that have no stated convention.
- **Read CI.** `.github/workflows/*.yml` is the most reliable statement of what "passing" means in
  this repo. Prefer it over everything above.
- **FVM:** if `.fvmrc` or `.fvm/` exists, every Dart and Flutter command is prefixed `fvm`. Never
  mix `fvm flutter` and bare `flutter` in one run.
- **Xcode:** discover the scheme with `xcodebuild -list` rather than guessing it from the folder
  name. If no simulator destination is available, run the build only and say in the report that
  tests were not run — do not silently skip them.
- **Unknown stack:** do not invent commands. Ask the user how the project is built and tested,
  then record the answer in `state.json` under `verification` so later steps and resumes reuse it.
