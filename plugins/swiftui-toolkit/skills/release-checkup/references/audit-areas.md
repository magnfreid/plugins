# Audit areas

One section per area, in the order the run uses. Each has **Covers**, **Starting points** and
**Not a finding**. An auditor reads only its own section.

## correctness — Correctness and robustness

**Covers:** bugs, crash risks (force unwraps, `try!`, `as!`, `fatalError`/`preconditionFailure`
reachable in release), error handling (errors swallowed by `try?` or empty `catch`), empty, error
and offline states, and behaviour that is inconsistent between screens.

**Starting points:**
- `grep -rn 'try!\|as!\|fatalError(\|preconditionFailure(\|\.first!\|\[0\]' --include=*.swift`
- `catch {` blocks with no handling.
- Views that load data with no error or empty branch.

**Not a finding:** `fatalError` in `required init?(coder:)` and in code paths compiled out of
release.

## architecture — Architecture and data flow

**Covers:** state ownership; `@State`, `@Binding`, `@Observable` and `@Environment` use;
unnecessary view updates and body recomputation; heavy work in `body`; concurrency (Swift 6 strict
concurrency, `@MainActor`, `Task` lifetimes); retain cycles.

**Starting points:**
- Read `SWIFT_VERSION`, `SWIFT_STRICT_CONCURRENCY` and `SWIFT_DEFAULT_ACTOR_ISOLATION` from
  `project.pbxproj` / `Package.swift` **before** judging any `@MainActor`. It is redundant under
  default MainActor isolation and required without it.
- `Task {` in views without cancellation on disappear.
- `[self]` / strong `self` captures in stored closures.
- Formatters, sorting or filtering inside `body`.

**Not a finding:** the architecture itself (MVVM or not) when the project's `CLAUDE.md` states it.

## code-health — Code health

**Covers:** duplication; dead code; naming of types, files and methods; consistency; deprecated
APIs; build warnings; missing documentation on public or non-obvious API; TODO and FIXME; debug
flags and preview or mock data reachable in release; leftover `print`s.

**Starting points:**
- `grep -rn 'TODO\|FIXME\|print(\|debugPrint(\|dump(' --include=*.swift`
- `#if DEBUG` balance.
- Mock or preview types referenced outside `#Preview` / `#if DEBUG`.
- **Build warnings need a from-scratch build:**
  `xcodebuild -scheme <scheme> -configuration Release -destination 'generic/platform=<platform>' -onlyUsePackageVersionsFromResolvedFile -derivedDataPath "${TMPDIR:-/tmp}/release-checkup-dd" clean build CODE_SIGNING_ALLOWED=NO 2>&1 | grep -E 'warning:|error:|BUILD (SUCCEEDED|FAILED)'`.
  Run it once per platform in `scope.md`, with `<platform>` as `iOS Simulator`, `macOS`,
  `watchOS Simulator`, `tvOS Simulator` or `visionOS Simulator`. A hardcoded iOS destination fails
  every app that does not build for iOS.
  `-onlyUsePackageVersionsFromResolvedFile` stops the build rewriting `Package.resolved`.
  No `BUILD SUCCEEDED` line means it did not build: record why under `Not checked`.
- Deprecated APIs: the build warnings, plus `doc-text.py` from `swiftui-toolkit:hig` on any
  suspicious API page.

**Not a finding:** style the project's formatter or linter config allows.

## security — Security and privacy

**Covers:** secrets in source; secrets in `UserDefaults` instead of Keychain; ATS exceptions;
sensitive data in logs; `PrivacyInfo.xcprivacy`; Info.plist usage descriptions; unused
entitlements; dependency licences; outdated dependencies.

**Starting points:**
- Grep for `apiKey|secret|token|password|Bearer` in sources and plists.
- `UserDefaults` writes of those keys.
- `NSAllowsArbitraryLoads` / `NSExceptionDomains`.
- `Logger`/`os_log`/`print` interpolating user data (OSLog string interpolation is private by
  default, but numbers and booleans are public).
- Every `NS*UsageDescription` against the APIs actually used.
- `*.entitlements` against capabilities used.
- `PrivacyInfo.xcprivacy` present, with required-reason APIs declared (doc:
  `bundleresources/privacy-manifest-files`).
- `Package.resolved` / `Podfile.lock`, with licence files in resolved checkouts and the latest tag
  per dependency via `git ls-remote --tags <url>` (read-only).

**Not a finding:** a key that is public by design (for example a client-side analytics key) when
the project says so.

## ui — UI, HIG and accessibility

**Load `swiftui-toolkit:hig` first and apply its Review rules.**

**Covers:** VoiceOver labels; Dynamic Type; contrast; Reduce Motion; dark mode; iPad and
orientation; localization (hardcoded strings, String Catalog gaps); custom controls where native
ones exist.

**Starting points:**
- `.font(.system(size:`
- `Color(red:` / hex initialisers in views.
- `Image(` without `accessibilityLabel` on interactive elements.
- `onTapGesture` on non-`Button` views.
- `Text("` literals in a project that has a `Localizable.xcstrings` (check its keys for missing
  translations).
- `withAnimation` without `accessibilityReduceMotion`.
- `UISupportedInterfaceOrientations` / device family against the layouts.

Cite the HIG slug in every finding.

**Not a finding:** a deviation the project records as deliberate.

## release — Release readiness

**Covers:** version and build numbers; app icon; launch screen; App Store Review Guidelines risks;
test gaps on critical paths; release build configuration.

**Starting points:**
- `xcodebuild -showBuildSettings -scheme <scheme> -configuration Release -onlyUsePackageVersionsFromResolvedFile` (read-only) for
  `MARKETING_VERSION`, `CURRENT_PROJECT_VERSION`, optimisation and
  `SWIFT_ACTIVE_COMPILATION_CONDITIONS`.
- Compare the version with the latest git tag.
- App icon asset complete (doc: `xcode/configuring-your-app-icon`).
- `UILaunchScreen` or a launch storyboard present.
- App Review Guidelines at `https://developer.apple.com/app-store/review/guidelines/` (this page is
  server-rendered HTML and fetches normally, unlike the docs) for login walls, account deletion,
  in-app purchase and placeholder content.
- Test targets covering the critical flows named in `scope.md`.

**Not a finding:** missing tests on purely presentational views (per
`dev-workflow:testing-doctrine`).
