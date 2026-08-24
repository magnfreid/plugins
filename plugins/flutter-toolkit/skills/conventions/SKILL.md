---
name: conventions
description: The default architectural conventions for Magnus's Flutter projects — BLoC + Freezed state, lib/ vs packages/ boundaries, go_router, mocktail, FVM. Load before planning or implementing any Flutter change so defaults are applied without being restated, and whenever asked what the Flutter conventions are.
---

# Flutter conventions

These are **defaults, not laws**. They apply unless overridden. Precedence, highest first:

1. An explicit instruction from Magnus in the current session.
2. The project's `CLAUDE.md` or `.claude/conventions/flutter.md`.
3. Existing patterns in the repo — if the codebase consistently does something else, mirror it and
   say so rather than converting the codebase mid-feature.
4. This file.

Departing from a default is fine. Departing silently is not: record it in the plan's
**Conventions applied** table with the reason.

## State management

- **BLoC + Freezed unions** is the default. Events are a union too.
- **Cubit** only when there are genuinely no events worth modelling — the state machine is purely
  setter-driven. "It's a small screen" is not a reason; "there is nothing to name as an event" is.
- Do not use `setState` for anything a widget doesn't exclusively own, and do not reach for
  Provider, Riverpod, GetX, or `ChangeNotifier` as a substitute for the above.
- One BLoC per feature unless two independent state machines genuinely coexist. Splitting a BLoC
  to reduce file size is not a reason to split it.
- Handlers use `on<Event>` / `emit.forEach`. No `yield*`, no pre-8.x APIs.

## Data classes

- **Freezed by default** for any immutable data class — domain models, DTOs, repository return
  types, value objects in `packages/<name>/` — not just BLoC state and events. If a class would
  otherwise need a hand-written `copyWith`, `==`/`hashCode`, or `toString`, make it `@freezed`
  instead.
- **Never hand-write `copyWith`, `==`, `hashCode`, or `toString`** for a data class Freezed could
  generate. Reaching for one by hand is the signal to convert the class, not a reason to keep
  going.
- A wire model that only needs `fromJson`/`toJson` can stay plain `@JsonSerializable`. The moment
  it also needs `copyWith` or value equality, combine `@freezed` with `json_serializable` rather
  than hand-rolling either.
- **Opt-outs:** a class that's genuinely mutable in place (not replaced on change) isn't a Freezed
  candidate — Freezed is for immutable data. Nor is a class with nothing to copy or compare, e.g.
  a static-method namespace.
- Same codegen rule applies: any file touched with `@freezed` needs `build_runner` before the
  change is done.

## Project layout

- **`lib/`** is UI only — widgets, BLoCs, view glue.
- **`packages/<name>/`** holds domain logic, repositories, data sources, pure Dart. Own
  `pubspec.yaml`, wired in by path dependency.
- The test for where code goes: if it can be unit-tested without importing Flutter, it belongs in a
  package.

## Networking

- **Dio**, wrapped behind a repository in a package. Widgets and BLoCs never see Dio types.
- Errors cross the package boundary as domain failures, not `DioException`.

## Navigation

- **go_router**, shell routes for tab scaffolds.
- Auth redirects live in a single `redirect` callback. Never scatter guards across route defs.

## Testing

- `bloc_test` for BLoCs and Cubits, widget tests for pages.
- **mocktail** for mocks — never mockito. `registerFallbackValue` for non-primitive matchers.
- **Tests ship in the same PR as the code they cover.** Required: every new BLoC or Cubit
  (transitions *and* error paths), every new repository or service public contract including its
  failure mapping, pure domain logic, and the ordering of catch clauses wherever a `_guard`-style
  method rethrows a typed exception before a catch-all.
- One widget test per new page, pumped through the **real page class** rather than its `View` —
  the page's provider wiring is where lifecycle bugs live and a `View`-level test cannot see them.
- **Assert against strings resolved from the l10n delegate**, never hardcoded English.
- Full coverage is not the goal: cover the seams whose breakage is silent and the paths a user
  actually walks. Details and patterns in `flutter-toolkit:testing`.

## Tooling

- **FVM**, stable channel. Always `fvm flutter ...` / `fvm dart ...`, never bare `flutter`.
- Codegen: `fvm dart run build_runner build --delete-conflicting-outputs` after touching any
  Freezed or json_serializable file.
- Verification order: `build_runner` → `fvm dart analyze` → `fvm flutter test`.

## Style

- One public class per file. Small private helpers may share the file.
- Extract a widget as soon as `build` passes ~50 lines. Composition over inheritance.
- `const` wherever legal.
- No `late` unless the exact initialization point can be named. Prefer `final` + constructor, or
  nullable with a check.
- No `print` — use the project's logger.

## Dependencies

Do not add a pub dependency inside a feature workflow. If one is genuinely needed, stop and raise
it with the alternative you considered. New dependencies are a decision, not an implementation
detail.
