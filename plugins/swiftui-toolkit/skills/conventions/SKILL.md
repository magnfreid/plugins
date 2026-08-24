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

## Structure

- Views are pure UI. No networking, no persistence, no business rules in a `body`.
- Services and stores live in `Core/`, screens in feature folders.
- Extract a subview as soon as `body` stops being readable at a glance.

## Design system

- Semantic tokens from `Core/DesignSystem/` for colour, typography, and spacing.
- No literal `Color(...)`, `.font(.system(size:))`, or magic padding numbers in feature code. If a
  token is missing, add it to the design system rather than inlining a value.

## Navigation

- `NavigationStack` with `navigationDestination(for:)`, driven programmatically through `AppRouter`.
- Routes are typed values, not strings.

## Localization

- Components accept `LocalizedStringKey`. No hardcoded user-facing strings anywhere in a view.

## Persistence

- SwiftData is the default for local persistence. Models stay free of view concerns; queries live
  behind a service rather than in `body`.

## Concurrency

- `async/await` with structured concurrency. UI-touching types are `@MainActor`.
- No completion handlers in new code, no `DispatchQueue.main.async` as a substitute for `@MainActor`.

## Verification

- Build the scheme and run the test target before declaring work done. Warnings introduced by the
  change count as failures.

## Dependencies

Do not add an SPM dependency inside a feature workflow. If one is genuinely needed, stop and raise
it with the alternative you considered.
