---
name: bloc
description: Flutter state management with BLoC/Cubit + Freezed. Trigger on any state or reactive logic in a Flutter app — "add a bloc for X", "write state for this feature", "handle loading/error state", Cubit vs BLoC decisions, BlocProvider/BlocBuilder/BlocListener usage, event transformers (droppable, debounce, restartable, sequential), and the build_runner codegen step after editing Freezed files.
---

# bloc

Conventions for state management in this Flutter stack: BLoC by default, Cubit for narrow cases, two state-shape patterns depending on the screen, Freezed for equality, codegen via build_runner.

## Cubit or BLoC?

Default to **BLoC**. Use **Cubit** only when:

- State is driven by an upstream stream (`authStateChanges`, connectivity, etc.) and there are no distinct user intents.
- You would otherwise write a BLoC with a single event that just calls `emit()`.

If the feature has user-triggered actions (submit, retry, toggle, refresh), use BLoC so events are first-class and testable.

## State shape: sealed union or status + data?

Two legitimate patterns. Pick per screen based on what the state has to hold. Both use Freezed for equality.

### Sealed union — discrete states with different data

Use when states are genuinely mutually exclusive and carry different data. Each case has its own shape.

**When to use:**

- Login, signup, form submission, onboarding steps.
- Screens where the UI is completely different across states (a spinner page → a result page).
- Any flow where "data from the previous state" shouldn't leak forward.

```dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'login_state.freezed.dart';

@freezed
sealed class LoginState with _$LoginState {
  const factory LoginState.initial() = LoginInitial;
  const factory LoginState.submitting() = LoginSubmitting;
  const factory LoginState.success() = LoginSuccess;
  const factory LoginState.failure(String message) = LoginFailure;
}
```

Name the generated classes publicly (`LoginInitial`, not `_Initial`). Dart 3 switch patterns need public names.

### Status enum + single class — data-heavy screens

Use when the screen carries substantial data that should persist across transitions, or when you want stale-while-revalidate behavior (show old data under a loading indicator).

**When to use:**

- List/feed screens with pagination, filters, search, pull-to-refresh.
- Forms with many fields where each transition touches a subset.
- Any screen where reloading should keep prior data visible.
- Small deltas are common (flipping a filter, updating one field).

```dart
enum TodoStatus { initial, loading, success, failure }

@freezed
class TodoState with _$TodoState {
  const factory TodoState({
    @Default(TodoStatus.initial) TodoStatus status,
    @Default(<Todo>[]) List<Todo> todos,
    Exception? exception,
  }) = _TodoState;
}
```

**The tradeoff:** this pattern admits invalid states (e.g., `status: success, exception: Exception(...)`). Handlers must clear stale fields on transitions:

```dart
emit(state.copyWith(status: TodoStatus.loading, exception: null));
```

Freezed still handles equality for you — no Equatable needed here either.

### Decision heuristic

If you find yourself duplicating a field (like `todos`) across most cases of a sealed union, switch to status + data. If you find yourself branching on `status` in a sprawling switch and the cases feel like they should be distinct types, switch to sealed union.

## Events — always sealed unions

There is no status-enum equivalent for events. Every user intent is a distinct action.

```dart
@freezed
sealed class LoginEvent with _$LoginEvent {
  const factory LoginEvent.submitted({
    required String email,
    required String password,
  }) = LoginSubmitted;
  const factory LoginEvent.resetRequested() = LoginResetRequested;
}
```

One file per event union: `login_event.dart`.

## BLoC structure

Use the `on<Event>(handler)` form. `mapEventToState` is legacy — never use it.

```dart
class LoginBloc extends Bloc<LoginEvent, LoginState> {
  LoginBloc({required AuthRepository repo})
      : _repo = repo,
        super(const LoginState.initial()) {
    on<LoginSubmitted>(_onSubmitted);
    on<LoginResetRequested>(_onResetRequested);
  }

  final AuthRepository _repo;

  Future<void> _onSubmitted(
    LoginSubmitted event,
    Emitter<LoginState> emit,
  ) async {
    emit(const LoginState.submitting());
    try {
      await _repo.signIn(email: event.email, password: event.password);
      emit(const LoginState.success());
    } on AuthException catch (e) {
      emit(LoginState.failure(e.message));
    }
  }

  void _onResetRequested(
    LoginResetRequested event,
    Emitter<LoginState> emit,
  ) {
    emit(const LoginState.initial());
  }
}
```

For a status-enum state, the same handler pattern applies — just use `copyWith`:

```dart
Future<void> _onLoadRequested(
  TodoLoadRequested event,
  Emitter<TodoState> emit,
) async {
  emit(state.copyWith(status: TodoStatus.loading, exception: null));
  try {
    final todos = await _repo.fetchAll();
    emit(state.copyWith(status: TodoStatus.success, todos: todos));
  } on Exception catch (e) {
    emit(state.copyWith(status: TodoStatus.failure, exception: e));
  }
}
```

Rules:

- Inject dependencies via constructor. Never instantiate repos/services inside a BLoC.
- Handlers are `Future<void>` if async, `void` otherwise.
- No business logic in handlers — delegate to the repo, translate outcomes to states.
- One public class per file; `LoginBloc` goes in `login_bloc.dart`.

## Event transformers

Transformers control how the BLoC processes events of a given type — debouncing, dropping, queuing, etc. They're passed as the `transformer` argument on `on<Event>()`.

### When to apply a transformer

Not every event needs one. Default (concurrent) is fine for most cases. Apply a transformer when the event has a specific concurrency or timing requirement:

- **Droppable** — submit buttons, login, save, purchase. The user taps while a request is in-flight; the duplicate should be ignored, not queued. This is the most common transformer you'll reach for.
- **Debounce** — search-as-you-type, text field validation. Wait for the user to stop typing before firing the handler. Typical duration: 300–500ms.
- **Restartable** — autocomplete, live search results. Like debounce but also cancels the previous in-flight handler when a new event arrives. Use when the old result is stale the moment the user types another character.
- **Sequential** — ordered writes, multi-step forms. Events must be processed one at a time, in order, with no dropping. Rarely needed — reach for it only when ordering guarantees matter.

If none of these apply, don't add a transformer. The default concurrent behavior is correct for independent, non-overlapping events like navigation or UI toggles.

### Using transformers — check the project first

**Before importing `bloc_concurrency` or writing a transformer, search the project for existing implementations.** Many projects (including boilerplate setups) ship pre-built transformers under names like `droppable()`, `debounce()`, `throttle()`, `restartable()`, or similar. Check:

1. `lib/core/` or `lib/shared/` or `packages/` for transformer files.
2. Any `bloc_transformers`, `event_transformers`, or similarly named files/directories.
3. Existing BLoCs in the project — see what they already use and import.

If the project has its own transformers, use those. If not, `bloc_concurrency` is the standard package:

```yaml
dependencies:
  bloc_concurrency: ^0.2.0
```

### Wiring transformers

Transformers go on the `on<Event>()` registration, not on the BLoC class itself:

```dart
import 'package:bloc_concurrency/bloc_concurrency.dart';

class LoginBloc extends Bloc<LoginEvent, LoginState> {
  LoginBloc({required AuthRepository repo})
      : _repo = repo,
        super(const LoginState.initial()) {
    on<LoginSubmitted>(
      _onSubmitted,
      transformer: droppable(),  // Ignore taps while login is in-flight
    );
    on<LoginResetRequested>(_onResetRequested); // No transformer needed
  }
  // ...
}
```

For debounce, you typically write a small helper that returns an `EventTransformer`:

```dart
EventTransformer<E> debounce<E>({
  Duration duration = const Duration(milliseconds: 300),
}) {
  return (events, mapper) =>
      events.debounceTime(duration).asyncExpand(mapper);
}
```

Or use the project's existing debounce transformer if one exists. Then apply it:

```dart
on<SearchQueryChanged>(
  _onSearchQueryChanged,
  transformer: debounce(duration: const Duration(milliseconds: 400)),
);
```

### Common pairings

| Event type | Transformer | Why |
|---|---|---|
| Form submit / login / save / purchase | `droppable()` | Prevent duplicate requests from button spam |
| Search text changed | `debounce()` or `restartable()` | Wait for typing to settle; cancel stale searches |
| Autocomplete / live results | `restartable()` | Cancel previous request when new input arrives |
| Pagination (load next page) | `droppable()` | Ignore scroll events while a page is loading |
| Pull-to-refresh | `droppable()` | One refresh at a time |
| Ordered queue (chat send, multi-step) | `sequential()` | Process in strict order, no concurrency |

### Decision rule

Ask: "What should happen if this event fires while the previous one is still being handled?"

- "Ignore it" → `droppable()`
- "Wait then fire" → debounce or `sequential()`
- "Cancel the old one, start fresh" → `restartable()`
- "Doesn't matter, they're independent" → no transformer (default)

## Cubit structure

For the narrow cases from above:

```dart
class AuthCubit extends Cubit<AuthState> {
  AuthCubit({required AuthRepository repo})
      : _repo = repo,
        super(const AuthState.unknown()) {
    _sub = _repo.authStateChanges.listen((user) {
      emit(user == null
          ? const AuthState.unauthenticated()
          : AuthState.authenticated(user));
    });
  }

  final AuthRepository _repo;
  late final StreamSubscription<User?> _sub;

  @override
  Future<void> close() async {
    await _sub.cancel();
    return super.close();
  }
}
```

Always cancel stream subscriptions in `close()`.

## Widget side

- `BlocProvider` — provide a BLoC above a subtree. Long-lived BLoCs wire in `bootstrap.dart` above `MaterialApp`. Feature-scoped BLoCs wire at the feature's route.
- `BlocBuilder` — rebuild UI from state. Use `buildWhen` when redraws are performance-sensitive.
- `BlocListener` — side effects only (snackbars, navigation, haptics). Never rebuild UI here.
- `BlocConsumer` — only when listener and builder share the same state scope.

**Pattern match on sealed union states** with Dart 3 switch expressions:

```dart
BlocBuilder<LoginBloc, LoginState>(
  builder: (context, state) => switch (state) {
    LoginInitial() => const LoginForm(),
    LoginSubmitting() => const CircularProgressIndicator(),
    LoginSuccess() => const SizedBox.shrink(),
    LoginFailure(:final message) => ErrorView(message: message),
  },
)
```

Sealed unions make the switch exhaustive — the compiler errors if a new case is added without updating the UI.

**Read fields directly on status-enum states**:

```dart
BlocBuilder<TodoBloc, TodoState>(
  builder: (context, state) {
    if (state.status == TodoStatus.failure) {
      return ErrorView(message: state.exception?.toString() ?? 'Unknown');
    }
    return Stack(
      children: [
        TodoList(todos: state.todos),
        if (state.status == TodoStatus.loading)
          const LinearProgressIndicator(),
      ],
    );
  },
)
```

Notice the stale-while-revalidate behavior — the list stays visible under the loading indicator. That's the reason to pick this pattern.

## Codegen (critical — do not skip)

After creating or modifying any `@freezed` file, run:

```
fvm dart run build_runner build --delete-conflicting-outputs
```

Without this, the `_$...` mixins don't exist and the project won't compile. When generating Freezed files, either run this command or flag it prominently so the user runs it. Do not leave the user with a broken build.

## BlocObserver

`bootstrap.dart` wires a `BlocObserver` in debug mode by default. Custom observers (logging, analytics) go there, not in feature code. A BLoC should never know it's being observed.

## Anti-patterns (do not do)

- **Equatable on Freezed classes** — Freezed handles equality; adding Equatable is redundant and breaks.
- **Business logic inside widgets** — `context.read<Bloc>().add(...)` followed by imperative branching. Move it into the BLoC.
- **`state.copyWith(...)` across cases of a sealed union** — `copyWith` exists per union case, not across them. To transition, construct the target case: `emit(LoginState.failure(e.message))`, not `emit(state.copyWith(...))`. This is a union-only gotcha — `copyWith` is the correct tool for status-enum states.
- **Leaking stale fields on status transitions** — with the status-enum pattern, always clear fields that no longer apply: `emit(state.copyWith(status: loading, exception: null))`. Otherwise invalid combinations creep in.
- **Cross-BLoC communication via direct references** — BLoCs talk to each other only through streams exposed by repositories. Never hold a reference to another BLoC.
- **Multiple BLoCs for one feature upfront** — start with one per feature. Split only when state domains have genuinely independent lifecycles.
- **`emit` after `close`** — async handlers can outlive the BLoC. Guard with `if (emit.isDone) return;` or let `on<E>` handle cancellation.

## File layout

```
lib/<feature>/bloc/
  <feature>_bloc.dart
  <feature>_event.dart
  <feature>_state.dart
```

Add a barrel `bloc.dart` only when the feature hosts 3+ BLoCs. For a single BLoC, the barrel is noise.
