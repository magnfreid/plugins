<!--
  Seed template for /flutter-toolkit:init-conventions.
  {{DOUBLE_BRACES}} are placeholders the seeder MUST resolve by reading the project.
  Never emit a placeholder, and never guess one — if it cannot be read, ask.
  Once seeded, the project owns this text. Edit it there, not here.
-->

## Flutter conventions

Binding rules for this project. Where the codebase already does something else consistently,
the codebase wins — say so rather than converting it mid-feature.

### Structure

```
lib/                  UI only — widgets, BLoCs, view glue
  app/router/         all route definitions; features own pages, not routes
  <feature>/          bloc/, view/, widgets/, models/
  bootstrap.dart      runApp; the only place a concrete implementation is named
packages/<name>/      domain logic, repositories, data sources, pure Dart
```

**No services, repositories, API clients, or domain logic in `lib/`.** The test for where code
goes: if it can be unit-tested without importing Flutter, it belongs in a package.
{{WORKSPACE_NOTE}}

`view/` holds one file by default, `<feature>_page.dart`. The page provides the BLoC and a public
`<Feature>View` renders it — both in that file. `View` is public deliberately: it is the seam a
widget test injects a scripted bloc through.

### Rules

- **BLoC + Freezed unions** for state, events included. Cubit only when there is genuinely nothing
  to name as an event — "it's a small screen" is not a reason. Never Provider, Riverpod, GetX, or
  `ChangeNotifier` as a substitute. No `setState` for anything a widget does not exclusively own.
- **Freezed for any immutable data class** — domain models, DTOs, repository return types, not
  just BLoC state. Never hand-write `copyWith`, `==`, `hashCode`, or `toString` for a class Freezed
  could generate; reaching for one by hand is the signal to convert the class.
- **Depend on `abstract interface class`, never a concrete implementation.** Implementations are
  named for their backing technology (`FirebaseAuthRepository`, `DioOrdersApi`). Every interface
  ships a `Fake*` in the same package.
- **Domain types at the boundary.** No vendor type — a `User`, a `DioException`, an SDK `Schema` —
  through a public interface. Failures cross as domain failures. Concrete implementations are wired
  in `bootstrap.dart` only.
- **Do not abstract on speculation.** A package earns its existence by having a plausible second
  implementation, or by being a distinct domain needing its own storage tree and access rules.
- **go_router**, shell routes for tab scaffolds, auth redirects in a single `redirect` callback —
  never scattered across route definitions.
- **No hardcoded user-facing strings.** Assert against strings resolved from the l10n delegate,
  never hardcoded English.
- **Line length 120** — the `dart format` default. Disable `lines_longer_than_80_chars` in the lint
  config rather than reformatting.
- **Tests ship in the same PR as the code they cover.** Required: every BLoC or Cubit (transitions
  *and* error paths), every repository or service contract including failure mapping, pure domain
  logic, and the ordering of catch clauses wherever a `_guard`-style method rethrows a typed
  exception before a catch-all. mocktail, never mockito. One widget test per page, pumped through
  the **real page class** rather than its `View` — provider wiring is where lifecycle bugs live.

### Verification

{{FVM_NOTE}}In order:

```
{{VERIFY_CHAIN}}
```

**A warning introduced by the change counts as a failure**, and the format check is a hard failure,
not a nicety — it is the cheapest CI red there is.

{{WORKSPACE_TEST_WARNING}}

