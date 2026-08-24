---
name: conventions
description: The default architectural conventions for Magnus's SwiftUI projects — @Observable state, design system tokens, NavigationStack + AppRouter, SwiftData, localization. Load before planning or implementing any SwiftUI or iOS change so defaults are applied without being restated, and whenever asked what the SwiftUI conventions are.
---

# SwiftUI conventions

These are **defaults, not laws**. They apply unless overridden. Precedence, highest first:

1. An explicit instruction from Magnus in the current session.
2. The project's `CLAUDE.md` or `.claude/conventions/swiftui.md`.
3. Existing patterns in the repo — mirror them rather than converting the codebase mid-feature.
4. This file.

Departing from a default is fine. Departing silently is not: record it in the plan's
**Conventions applied** table with the reason.

## State

- `@Observable` for shared and view-scoped models. Inject with `.environment()`, read with
  `@Environment(StoreName.self)`.
- `@State` for state a single view exclusively owns.
- **Never** `ObservableObject`, `@Published`, `@StateObject`, `@ObservedObject`, or
  `@EnvironmentObject`. These are the pre-Observation API and must not appear in new code.
- A screen with non-trivial local logic gets its own `@Observable` view model, injected via
  `.environment()` — not a pile of `@State` in the view.
- Stores are instantiated once at the app entry point with `@State` and injected with
  `.environment()`. **Never singletons.**

## Structure

- Views are pure UI. No networking, no persistence, no business rules in a `body`.
- Services and stores live in `Core/`, screens in feature folders.
- Extract a subview as soon as `body` stops being readable at a glance.

## Design system

- Semantic tokens from `Core/DesignSystem/` for colour, typography, and spacing; styles in
  `Core/Styles/`; wrapper views in `Core/Components/`.
- No literal `Color(...)`, `.font(.system(size:))`, or magic padding numbers in feature code. If a
  token is missing, add it to the design system rather than inlining a value.
- Details, and how a design handoff turns into tokens: `swiftui-toolkit:design-tokens`.

## Navigation

- `NavigationStack` with `navigationDestination(for:)`, driven programmatically through `AppRouter`.
- Routes are typed values, not strings.
- Bind with `@Bindable var router = router` in views that drive the path. Inject the router through
  the environment — never prop-drill it.
- **Never** `NavigationLink(destination:)` for programmatic navigation. Go through the router.

## Localization

- Components accept `LocalizedStringKey`. No hardcoded user-facing strings anywhere in a view.
- Keys live in `Resources/Localizable.xcstrings`. Use symbol keys with `extractionState: "manual"`
  where the project supports them (`Text(.loginEmailPlaceholder)`), otherwise dot notation
  (`login.email.placeholder`). Never repeat a literal across views.

## Persistence

- SwiftData is the default for local persistence. Models stay free of view concerns; queries live
  behind a service rather than in `body`.
- Keep it in its own `SwiftData/` group so it can be removed wholesale if the app does not need it:
  models in `SwiftData/Models/`, the container in `SwiftData/AppModelContainer.swift`. Mark the
  module `[REMOVABLE]` in headers and plan docs when it is optional.
- Inject the `ModelContainer` at the app entry point. No direct `ModelContext` access from a view.
- **With CloudKit:** never `@Attribute(.unique)`; every property either has a default or is
  optional; every relationship is optional. These are hard requirements, not preferences —
  violating them fails at sync time, not at compile time.

## Concurrency

- `async/await` with structured concurrency. UI-touching types are `@MainActor`.
- No completion handlers in new code, no `DispatchQueue.main.async` as a substitute for `@MainActor`.

## Testing

Doctrine — what to test and why — is `dev-workflow:testing-doctrine`. Swift patterns are
`swiftui-toolkit:testing`. In short: stores, services, and domain logic are required; a screen test
drives the real view with its environment injected; UI tests only for what a unit test cannot reach.

## Verification

- Build the scheme and run the test target before declaring work done. Warnings introduced by the
  change count as failures.
- If SwiftLint is installed, it must report zero warnings and zero errors before committing.
- Discover the scheme with `xcodebuild -list` rather than guessing it. If no simulator destination
  is available, build only and *say* that tests were not run — never silently skip them.

## Dependencies

Do not add an SPM dependency inside a feature workflow. If one is genuinely needed, stop and raise
it with the alternative you considered.
