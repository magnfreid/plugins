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

- **`lib/`** is UI only — widgets, BLoCs, view glue. No services, repositories, API clients, or
  domain logic.
- **`packages/<name>/`** holds domain logic, repositories, data sources, pure Dart. Each has its
  own `pubspec.yaml`.
- Members are wired as a **Dart workspace**, not path dependencies: the root `pubspec.yaml` lists
  every member explicitly under `workspace:` (globs are not supported) *and* declares each as a
  dependency; every member sets `resolution: workspace`.
- First test for where code goes: if it can be unit-tested without importing Flutter, it belongs in
  a package.

## Feature structure

A feature is `lib/<feature>/`, with `bloc/`, `view/`, `widgets/`, `models/`, `extensions/` as
needed.

**`view/` holds exactly one file by default: `<feature>_page.dart`.** A second view file only when
the feature genuinely has a second distinct top-level page.

**The page provides the BLoC; a public `<Feature>View` renders it — both in the same file.** No
separate `_view.dart`. `View` is public deliberately: it is the seam a widget test injects a
scripted bloc through without going via the page's own provider.

```dart
class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => HomeBloc(),
      child: const HomeView(),
    );
  }
}

class HomeView extends StatelessWidget {
  const HomeView({super.key});

  @override
  Widget build(BuildContext context) {
    // actual UI here
  }
}
```

**Extraction.** Move a widget to `widgets/` as a public class — even if used once — as soon as it is
*semantically distinct*: a self-contained piece of UI with its own internal structure. A drawer
menu, a map control overlay, a settings section, a card with non-trivial content.

Keep a private `_Widget` in the page file only for genuinely small helpers: a styled divider, a
single row, a thin wrapper. Past ~40–50 lines, or more than a couple of parameters, promote it.

The target is a `<feature>_page.dart` that fits on one screen and reads like a layout outline
rather than an implementation. If you cannot see the page's composition at a glance, something in
it wants extracting.

**Features own pages, not routes.** Route definitions stay centralized in `lib/app/router/`.

## Modularity & interfaces

Build for replaceability. Anything that talks to the outside world — an SDK, a vendor API, a
platform service — sits behind an interface the project owns.

- **One package per capability vendor.** Exactly one package may import an SDK that is itself a
  swappable *capability* — a specific vendor's take on a product decision, where a different vendor
  is a real alternative (`firebase_auth` → `auth_repository`, an AI SDK → `ai_client`). If a second
  package needs to import that SDK, the boundary is in the wrong place.
- **Shared infrastructure is one package per domain, not one package total.** Some SDKs are not a
  capability choice at all — they are the plumbing everything sits on. A document database is where
  things are stored, not "our storage vendor, pending a swap." Forcing a single owner across
  unrelated domains means either merging domains that do not belong together, or inventing a
  generic wrapper that loses real capabilities the concrete SDK offers — cache-versus-server read
  semantics, for instance. So each domain that needs it gets its own package
  (`consent_repository`, `usage_repository`, …), each owning its own document tree and its own
  slice of the security rules.

  The question is not "how many packages import this SDK." It is **"is this SDK the product
  decision, or just where we happen to store something."** Getting it wrong in either direction
  costs: forcing shared infrastructure through one gate produces an unrelated-domain merger or a
  lossy wrapper; treating a real capability vendor as shared infrastructure puts a second
  swap-out site where there should be exactly one.
- **Depend on `abstract interface class`, never a concrete implementation.** Implementations are
  named for their backing technology — `FirebaseAuthRepository`, `DioOrdersApi`.
- **Every interface ships a `Fake*` implementation in the same package**, for tests and for UI work
  that should not need a network or burn quota.
- **Domain types at the boundary.** Never leak a vendor type — `User`, `DioException`, a vendor's
  `Schema` — through a public interface. Translate at the edge; failures cross as domain failures.
- **Express policy as domain concepts, not magic strings.** `AiModelTier.fast` at the call site,
  not `'vendor-model-3.5-flash'`.
- **Wire concrete implementations in `bootstrap.dart` only.** Feature code receives interfaces.

**Do not abstract on speculation.** A package earns its existence by having a plausible second
implementation — a different vendor, or a fake — or, for shared infrastructure, a distinct domain
that needs its own storage tree and access rules. All of the above is about seams that already
have a known second case, not indirection for its own sake.

## Bootstrap

`runApp` lives in `bootstrap.dart`. Long-lived repositories and services are constructed there and
provided above `MaterialApp`, usually via `RepositoryProvider`; `BlocObserver` is wired in debug
builds. It is the only place concrete implementations are named.

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
- Verification order: `build_runner` (only if codegen input changed) → `fvm flutter analyze` →
  `fvm dart format --set-exit-if-changed lib packages test` → `fvm flutter test` → `fvm flutter
  test` inside **each** `packages/<member>/` that has a `test/`.
- **The root test run does not descend into workspace members.** A repo that keeps its domain
  logic in `packages/` will report green having run a fraction of its suite. Iterate the packages
  explicitly, or put the whole chain in a `scripts/verify.sh` and run that.
- The format check is a hard failure, not a nicety — it is the cheapest CI red there is.

## Style

- One public class per file. Small private helpers may share the file.
- Composition over inheritance for widgets. Extraction thresholds are under **Feature structure**.
- **Line length 120** — the `dart format` default. Do not set a custom override; disable
  `lines_longer_than_80_chars` in the lint config rather than reformatting to 80.
- **Dot shorthands wherever the type is inferable** — `.bold`, not `FontWeight.bold`. Assumes
  Dart >= 3.10.
- **`public_member_api_docs` is enabled per package**, not in the root `lib/`. Every public member
  in `packages/<name>/` carries a `///` doc comment; feature code in `lib/` does not have to.
- `const` wherever legal.
- No `late` unless the exact initialization point can be named. Prefer `final` + constructor, or
  nullable with a check.
- No `print` — use the project's logger.

## Dependencies

Do not add a pub dependency inside a feature workflow. If one is genuinely needed, stop and raise
it with the alternative you considered. New dependencies are a decision, not an implementation
detail.
