---
name: testing
description: Flutter testing with bloc_test, mocktail, and widget tests. Trigger on any test work — "write a test for", "bloc_test", "widget test", "mock this repo", "test this bloc", "add tests", or when a BLoC / repo / widget has been created or modified and needs coverage.
---

# testing

Conventions for tests in this Flutter stack: `bloc_test` for BLoCs/Cubits, widget tests for interaction and rendering logic, `mocktail` for mocks (never `mockito`).

## What to test

**Tests ship in the same PR as the code they cover.** This reverses an earlier "skip tests unless asked" default. That default was dropped after a feature shipped a crash-on-open to a real device — nothing in the repo mounted a page, so nothing caught it.

**Required.** A change that adds any of these is not done without tests:

- **Every new BLoC or Cubit** — state transitions *and* error paths.
- **Every new repository or service public contract**, including its failure mapping.
- **Pure domain logic** — gap detection, schema translation, failure mappers; anything with branches and no Flutter import.
- **Catch-clause ordering**, anywhere a `_guard`-style method rethrows a typed exception before a catch-all. See below — this is the one that breaks silently.

**Default.** One widget test per new page, pumped through the **real page class** rather than its `View`. Add the page's primary interaction where it has one.

**Not required.** Pure layout widgets, and generated code (`*.freezed.dart`, `app_localizations*.dart`).

**Full coverage is explicitly not the goal.** Cover the seams whose breakage is silent, and the paths a user actually walks. Skipping something genuinely churny is fine — say so in the PR's open items rather than writing a test nobody trusts.

## Where tests live

```
<project-root>/
  test/                    # App-level unit + widget tests (mirrors lib/)
    integration/           # Integration tests
  packages/<pkg>/
    test/                  # Each workspace package has its own test/
```

Feature tests mirror `lib/<feature>/` structure: tests for `lib/login/bloc/login_bloc.dart` go in `test/login/bloc/login_bloc_test.dart`.

## bloc_test

Use `blocTest<BlocType, StateType>`. Structure: `setUp`, `build`, `act`, `expect`, optional `verify`.

```dart
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class _MockAuthRepo extends Mock implements AuthRepository {}

void main() {
  late AuthRepository repo;

  setUp(() {
    repo = _MockAuthRepo();
  });

  group('LoginBloc', () {
    blocTest<LoginBloc, LoginState>(
      'emits [submitting, success] on successful submit',
      setUp: () {
        when(() => repo.signIn(
              email: any(named: 'email'),
              password: any(named: 'password'),
            )).thenAnswer((_) async {});
      },
      build: () => LoginBloc(repo: repo),
      act: (bloc) => bloc.add(
        const LoginSubmitted(email: 'a@b.com', password: 'pw'),
      ),
      expect: () => [
        const LoginState.submitting(),
        const LoginState.success(),
      ],
      verify: (_) {
        verify(() => repo.signIn(email: 'a@b.com', password: 'pw')).called(1);
      },
    );

    blocTest<LoginBloc, LoginState>(
      'emits [submitting, failure] when repo throws',
      setUp: () {
        when(() => repo.signIn(
              email: any(named: 'email'),
              password: any(named: 'password'),
            )).thenThrow(AuthException('bad creds'));
      },
      build: () => LoginBloc(repo: repo),
      act: (bloc) => bloc.add(
        const LoginSubmitted(email: 'a@b.com', password: 'wrong'),
      ),
      expect: () => [
        const LoginState.submitting(),
        const LoginState.failure('bad creds'),
      ],
    );
  });
}
```

## mocktail patterns

**`registerFallbackValue` for any custom type** used with `any()` / `captureAny()`:

```dart
void main() {
  setUpAll(() {
    registerFallbackValue(const LoginSubmitted(email: '', password: ''));
  });
  // ...
}
```

Without this, `when(() => bloc.add(any()))` throws at runtime because mocktail can't construct a fallback for `LoginEvent`.

**Named arguments require `named:`**:

```dart
when(() => repo.signIn(
      email: any(named: 'email'),
      password: any(named: 'password'),
    )).thenAnswer((_) async {});
```

Forgetting `named: 'foo'` on a named-arg `any()` silently fails to match. This is the single most common mocktail bug.

**No codegen**. No `@GenerateMocks`, no `build_runner` for tests. Mocks are hand-written: `class _MockFoo extends Mock implements Foo {}`.

## Catch-clause ordering

A `_guard`-style wrapper that rethrows a typed failure before a catch-all is order-dependent, and getting the order wrong fails *silently*:

```dart
Future<T> _guard<T>(Future<T> Function() op) async {
  try {
    return await op();
  } on AuthException {
    rethrow;                        // must come first
  } catch (_) {
    throw const AuthException.unknown();
  }
}
```

Swap those two clauses and every typed failure collapses to `unknown`. The suite stays green, the analyzer says nothing, and the UI starts showing a generic error for causes it used to name. This has been a real bug more than once — it is worth a dedicated test on every `_guard` in the codebase.

**The test must fail if the clauses are swapped**, which means asserting the *specific* failure:

```dart
test('rethrows a typed failure instead of remapping it to unknown', () async {
  when(() => source.signIn(any(), any()))
      .thenThrow(const AuthException.wrongPassword());

  await expectLater(
    repo.signIn('a@b.com', 'pw'),
    throwsA(isA<AuthException>().having((e) => e.kind, 'kind', AuthKind.wrongPassword)),
  );
});
```

`throwsA(isA<AuthException>())` on its own is **not** enough — the catch-all throws that same type, so the loose matcher passes in both orderings and pins nothing. Assert the discriminating field.

## Widget tests

There are two levels here and they catch different bugs. Know which one you are writing.

### Page level — the required default

Pump the **real page class**. The page is where `BlocProvider`, `RepositoryProvider`, and `initState` wiring lives, and that wiring is what breaks at runtime. Mock the *repositories* the page's bloc depends on, not the bloc itself — a test that replaces the bloc has replaced the thing it was supposed to prove.

```dart
testWidgets('LoginPage opens and renders its form', (tester) async {
  final repo = _MockAuthRepo();
  final l10n = await AppLocalizations.delegate.load(const Locale('en'));

  await tester.pumpWidget(
    MaterialApp(
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: RepositoryProvider<AuthRepository>.value(
        value: repo,
        child: const LoginPage(),
      ),
    ),
  );
  await tester.pump();

  expect(find.text(l10n.loginSignInButton), findsOneWidget);
});
```

A page-level test that merely opens the page is worth writing even with no assertion beyond "it rendered" — that is precisely the crash the skip-tests default used to let through.

### View level — for state rendering

The page delegates to a public `<Feature>View` in the same file specifically so a test can inject a scripted bloc without going through the page's own provider. Use this to cover per-state rendering:

```dart
class _MockLoginBloc extends MockBloc<LoginEvent, LoginState> implements LoginBloc {}

testWidgets('shows the error message when login fails', (tester) async {
  final bloc = _MockLoginBloc();
  final l10n = await AppLocalizations.delegate.load(const Locale('en'));

  whenListen(
    bloc,
    Stream.fromIterable([
      const LoginState.initial(),
      const LoginState.failure(LoginError.invalidCredentials),
    ]),
    initialState: const LoginState.initial(),
  );

  await tester.pumpWidget(
    MaterialApp(
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      home: BlocProvider<LoginBloc>.value(value: bloc, child: const LoginView()),
    ),
  );
  await tester.pump(); // let the stream emit

  expect(find.text(l10n.loginInvalidCredentials), findsOneWidget);
});
```

Wrapping the *page* in an outer `BlocProvider.value` does **not** substitute the bloc — the page builds its own inside, and the inner provider wins. That test passes while proving nothing about the mock. Inject at the `View`, or mock the repositories and let the page build its bloc for real.

### Assert against resolved localizations, never hardcoded English

`expect(find.text('Invalid credentials'), ...)` breaks the moment the copy is reworded or the test runs under another locale, and it silently asserts nothing about the l10n wiring. Load the delegate and assert against the resolved string, as both examples above do.

**`pump` vs `pumpAndSettle`**:

- `pump()` — advances one frame. Use when the number of frames to wait is known.
- `pumpAndSettle()` — pumps until no frames are scheduled. Use for animations, `FutureBuilder`, anything with unknown timing. **Will hang on infinite animations** (shimmer loops, pulsing indicators). In those cases use `pump(Duration)` with a specific timeout.

## Running tests

Before pushing:

```
fvm flutter analyze
fvm flutter test
```

Each workspace package runs its own tests from its own directory. The root `flutter test` does not recurse into `packages/<pkg>/test/` — CI should iterate per package.

## Anti-patterns (do not do)

- **`mockito` or `build_runner`-generated mocks** — this project is mocktail-only. Never `@GenerateMocks`.
- **Shared state between tests** — create fresh mocks/blocs in `setUp` or `build:`. Reusing instances causes order-dependent failures.
- **Pumping without asserting** — `await tester.pump()` with no following `expect` proves nothing and hides timing bugs.
- **Subscribing to `bloc.stream` manually** — use `bloc_test`'s `expect:`, which handles timing and diffing correctly.
- **Hardcoded English in `find.text`** — assert against strings resolved from the l10n delegate. A hardcoded literal breaks on a copy edit and proves nothing about localization wiring.
- **Loose exception matchers** — `throwsA(isA<SomeException>())` where a catch-all throws the same type. Assert the field that distinguishes them.
- **Widget tests that hit real I/O** — always mock at the BLoC or repo boundary. A widget test should never touch network, disk, or platform channels.
- **Golden tests without pinned theme/locale/font** — they flake on CI. Either pin everything or skip goldens.
- **`equals(const LoginState.failure('x'))` matchers with Equatable** — Freezed handles equality directly; bloc_test's `expect:` compares with `==`, which Freezed generates correctly. No extra matcher library needed.
