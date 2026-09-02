<!--
  Seed template for /swiftui-toolkit:init-conventions.
  {{DOUBLE_BRACES}} are placeholders the seeder MUST resolve by reading the project.
  Never emit a placeholder, and never guess one — if it cannot be read, ask.
  Once seeded, the project owns this text. Edit it there, not here.
-->

## SwiftUI conventions

Binding rules for this project. Where the codebase already does something else consistently,
the codebase wins — say so rather than converting it mid-feature.

### Structure

```
{{APP_DIR}}/
  App/              entry point, AppRouter
  Core/
    DesignSystem/   Color, Font, Spacing tokens
    Styles/         ButtonStyle, ViewModifier
    Components/     wrapper views over system controls
    Services/       networking, persistence, platform access
  Features/<Name>/  one folder per screen; views + its @Observable store
  Resources/        {{STRINGS_FILE}}
```

### Rules

- **State is `@Observable`.** Never `ObservableObject`, `@Published`, `@StateObject`,
  `@ObservedObject`, or `@EnvironmentObject` — that is the pre-Observation API and must not appear
  in new code. `@State` only for state a single view exclusively owns.
- **Stores are injected, never singletons.** Created once at the app entry point with `@State`,
  passed with `.environment()`, read with `@Environment(StoreName.self)`.
- {{ACTOR_ISOLATION_RULE}}
- **Views are pure UI.** No networking, no persistence, no business rules in a `body`.
- **Navigation goes through `AppRouter`** — `NavigationStack` with `navigationDestination(for:)`,
  routes as typed values, never strings. Never `NavigationLink(destination:)` for programmatic
  navigation.
- **No literal styling in feature code.** No `Color(...)`, no `.font(.system(size:))`, no magic
  padding numbers. If a token is missing, add it to `Core/DesignSystem/` — that is part of the
  work, not a follow-up.
- **No hardcoded user-facing strings**, including accessibility labels. Keys live in
  `{{STRINGS_FILE}}`.
- **`async`/`await` only.** No completion handlers in new code, no `DispatchQueue.main.async`
  standing in for `@MainActor`.
- **Tests ship in the same PR as the code they cover.** Required: every store, every service
  contract including how it maps failures, and pure domain logic.

### Verification

Run before declaring work done, and never claim a result you did not see:

```
{{BUILD_COMMAND}}
{{TEST_COMMAND}}
```

**A warning introduced by the change counts as a failure.** That single rule replaces a list of
banned APIs: it catches next year's deprecations too, and it cannot go stale.

A claim about warnings requires a **clean** build. An incremental build reports nothing for a file
it did not recompile.{{LINT_LINE}}

### Reference

Longer-form patterns live in `.claude/reference/`. Read the one you need rather than reconstructing
it: {{REFERENCE_LIST}}
