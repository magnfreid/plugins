---
name: scaffold-feature
description: Scaffold a new Flutter feature at lib/<feature>/ with bloc, view, widgets, models, and register its route in lib/app/router/routes.dart.
argument-hint: "<feature_name>"
---

# /scaffold-feature

Scaffold a new feature under `lib/<feature>/` following the boilerplate conventions, and register its route centrally.

## Arguments

Feature name in `$ARGUMENTS`. Must be snake_case (e.g. `login`, `user_profile`). Reject names with spaces, hyphens, or uppercase — stop and ask the user to rename.

Derive:

- `<feature>` — the argument verbatim (snake_case), used for file names and route path.
- `<Feature>` — PascalCase conversion (e.g. `user_profile` → `UserProfile`), used for class names.

## Before you act

1. Read the project's `pubspec.yaml` to get the Dart package name. You need it for imports into `routes.dart`.
2. Confirm `lib/app/router/routes.dart` exists. If not, the project is not using the expected layout — stop and explain.
3. Confirm `lib/<feature>/` does not already exist. If it does, stop and ask whether to overwrite.

## Files to create

Create this structure under `lib/<feature>/`:

```
bloc/
  <feature>_bloc.dart
  <feature>_event.dart
  <feature>_state.dart
view/
  <feature>_page.dart
widgets/
  .gitkeep
models/
  .gitkeep
```

### `<feature>_state.dart`

Starter is a sealed union with `initial`. See the `bloc` skill for when the status-enum pattern is better — the user can swap shapes before running codegen.

```dart
import 'package:freezed_annotation/freezed_annotation.dart';

part '<feature>_state.freezed.dart';

@freezed
sealed class <Feature>State with _$<Feature>State {
  const factory <Feature>State.initial() = <Feature>Initial;
}
```

### `<feature>_event.dart`

```dart
import 'package:freezed_annotation/freezed_annotation.dart';

part '<feature>_event.freezed.dart';

@freezed
sealed class <Feature>Event with _$<Feature>Event {
  const factory <Feature>Event.started() = <Feature>Started;
}
```

### `<feature>_bloc.dart`

```dart
import 'package:bloc/bloc.dart';

import '<feature>_event.dart';
import '<feature>_state.dart';

class <Feature>Bloc extends Bloc<<Feature>Event, <Feature>State> {
  <Feature>Bloc() : super(const <Feature>State.initial()) {
    on<<Feature>Started>(_onStarted);
  }

  void _onStarted(
    <Feature>Started event,
    Emitter<<Feature>State> emit,
  ) {
    // TODO: implement
  }
}
```

### `<feature>_page.dart`

```dart
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../bloc/<feature>_bloc.dart';
import '../bloc/<feature>_state.dart';

class <Feature>Page extends StatelessWidget {
  const <Feature>Page({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => <Feature>Bloc(),
      child: BlocBuilder<<Feature>Bloc, <Feature>State>(
        builder: (context, state) => switch (state) {
          <Feature>Initial() => const Scaffold(
              body: Center(child: Text('<Feature>')),
            ),
        },
      ),
    );
  }
}
```

## Edit `lib/app/router/routes.dart`

Three changes:

1. Add the import at the top:
   ```dart
   import 'package:<project_name>/<feature>/view/<feature>_page.dart';
   ```

2. Add constants to the `Routes` and `RouteNames` classes:
   ```dart
   static const <feature> = '/<feature>';   // in Routes
   static const <feature> = '<feature>';    // in RouteNames
   ```

3. Append a `GoRoute` to `appRoutes`:
   ```dart
   GoRoute(
     path: Routes.<feature>,
     name: RouteNames.<feature>,
     builder: (context, state) => const <Feature>Page(),
   ),
   ```

If the feature should live inside a shell route or nested under another route, the user will move it after — default to top-level.

## After you act

Report exactly what was created and edited. Then remind the user to run:

```
fvm dart run build_runner build --delete-conflicting-outputs
```

Without this the `_$...` Freezed mixins don't exist and the new files won't compile. Do not leave the user with a broken build.

## Do not

- Scaffold tests — this is minor work; per the testing rule, skip unless asked.
- Create placeholder widgets inside `widgets/` or model stubs inside `models/`. Leave those folders empty (with `.gitkeep`).
- Provide the BLoC above `MaterialApp` in `bootstrap.dart` — feature-scoped BLoCs are provided at the page level, as shown.
