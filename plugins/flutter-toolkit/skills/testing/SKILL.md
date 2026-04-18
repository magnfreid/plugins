---
name: testing
description: Flutter testing with bloc_test, mocktail, and widget tests. Trigger on any test work — "write a test for", "bloc_test", "widget test", "mock this repo", "test this bloc", "add tests", or when a BLoC / repo / widget has been created or modified and needs coverage.
---

# testing

Conventions for tests in this Flutter stack: `bloc_test` for BLoCs/Cubits, widget tests for interaction and rendering logic, `mocktail` for mocks (never `mockito`).

## What to test

From the project rules:

- **BLoCs/Cubits** — `bloc_test` covering state transitions and error paths. Required for non-trivial state logic.
- **Repositories/services** — unit tests for public contracts and error paths.
- **Widgets** — widget tests for meaningful interaction or rendering logic. Skip purely decorative widgets.
- **Minor/medium work** — skip tests unless asked.

When generating a new BLoC or repository as part of non-trivial work, generate its tests too unless told otherwise.

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

## Widget tests

Use `MockBloc` + `whenListen` from `bloc_test` to script bloc state:

```dart
import 'package:bloc_test/bloc_test.dart';

class _MockLoginBloc extends MockBloc<LoginEvent, LoginState> implements LoginBloc {}

void main() {
  setUpAll(() {
    registerFallbackValue(const LoginState.initial());
    registerFallbackValue(const LoginSubmitted(email: '', password: ''));
  });

  testWidgets('shows error when login fails', (tester) async {
    final bloc = _MockLoginBloc();
    whenListen(
      bloc,
      Stream.fromIterable([
        const LoginState.initial(),
        const LoginState.failure('Invalid credentials'),
      ]),
      initialState: const LoginState.initial(),
    );

    await tester.pumpWidget(
      MaterialApp(
        home: BlocProvider<LoginBloc>.value(
          value: bloc,
          child: const LoginPage(),
        ),
      ),
    );

    await tester.pump(); // let the stream emit
    expect(find.text('Invalid credentials'), findsOneWidget);
  });
}
```

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
- **Widget tests that hit real I/O** — always mock at the BLoC or repo boundary. A widget test should never touch network, disk, or platform channels.
- **Golden tests without pinned theme/locale/font** — they flake on CI. Either pin everything or skip goldens.
- **`equals(const LoginState.failure('x'))` matchers with Equatable** — Freezed handles equality directly; bloc_test's `expect:` compares with `==`, which Freezed generates correctly. No extra matcher library needed.
