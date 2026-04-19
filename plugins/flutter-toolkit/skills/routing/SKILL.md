---
name: routing
description: Flutter navigation with go_router. Trigger on any routing or navigation work — "add a route", "navigate to X", "go_router", nested routes, shell routes (bottom nav), auth redirects, typed routes, passing data between screens, or deep linking.
---

# routing

Conventions for navigation in this Flutter stack: `go_router`, declarative routes, the entire navigation tree centralized under `lib/app/router/` so the full structure is visible in one place. Features own their pages; the router owns routes.

## Declarative over imperative

Never use `Navigator.push` / `Navigator.pop` in feature code. Define the destination as a route, then navigate by name or path:

```dart
context.go('/settings');
context.goNamed('settings');
context.push('/settings/privacy');  // stacks on top, preserves prior route
context.pop();                      // returns from the top of the current stack
```

`go` replaces the current stack at that level; `push` stacks on top. Most transitions should be `go` — `push` only when you genuinely want to stack.

## File layout

Navigation lives in its own folder, separate from feature code. The whole nav tree reads top-to-bottom in `routes.dart`.

```
lib/app/router/
  app_router.dart    # GoRouter construction, shell routes, redirects
  routes.dart        # All GoRoute definitions + path/name constants
```

Features own their **pages**, not their routes. Pages live in `lib/<feature>/view/`; routes that point to them live in `lib/app/router/routes.dart`.

**Why this shape:** you can scan one file and see every destination in the app, plus how they nest. When debugging "why doesn't this link work," the answer is in one place. When reviewing auth behavior, all the guards are visible together.

### `routes.dart`

Keep every route and every name/path constant here. Each route is a record tuple with named `name` and `path` parameters, bundled under `AppRoutes`:

```dart
// lib/app/router/routes.dart
import 'package:go_router/go_router.dart';

import 'package:flutter_starter/home/view/home_page.dart';
import 'package:flutter_starter/login/view/login_page.dart';
import 'package:flutter_starter/settings/view/settings_page.dart';

abstract final class AppRoutes {
  static const ({String name, String path}) login = (name: 'login', path: '/login');
  static const ({String name, String path}) home = (name: 'home', path: '/');
  static const ({String name, String path}) settings = (name: 'settings', path: '/settings');
}

final appRoutes = <RouteBase>[
  GoRoute(
    path: AppRoutes.login.path,
    name: AppRoutes.login.name,
    builder: (context, state) => const LoginPage(),
  ),
  GoRoute(
    path: AppRoutes.home.path,
    name: AppRoutes.home.name,
    builder: (context, state) => const HomePage(),
    routes: [
      GoRoute(
        path: 'settings',
        name: AppRoutes.settings.name,
        builder: (context, state) => const SettingsPage(),
      ),
    ],
  ),
];
```

`abstract final class` prevents instantiation — `AppRoutes` is a namespace holding route tuples with both `name` and `path` bundled together.

### `app_router.dart`

Constructs the `GoRouter`, wires redirects and shell routes:

```dart
// lib/app/router/app_router.dart
import 'package:flutter/widgets.dart';
import 'package:go_router/go_router.dart';

import 'routes.dart';

class AppRouter {
  static GoRouter build({required AuthCubit authCubit}) => GoRouter(
        initialLocation: AppRoutes.home.path,
        routes: appRoutes,
        redirect: (context, state) => _authGuard(state, authCubit),
        refreshListenable: GoRouterRefreshStream(authCubit.stream),
      );

  static String? _authGuard(GoRouterState state, AuthCubit authCubit) {
    final isAuthed = authCubit.state is AuthAuthenticated;
    final isLoggingIn = state.matchedLocation == AppRoutes.login.path;

    if (!isAuthed && !isLoggingIn) return AppRoutes.login.path;
    if (isAuthed && isLoggingIn) return AppRoutes.home.path;
    return null;
  }
}
```

`MaterialApp.router` in `app.dart` consumes this via `AppRouter.build(authCubit: ...)`.

## Passing data

Three mechanisms, in order of preference:

1. **Path parameters** — entity IDs and intrinsic identifiers. Part of the URL.
   ```dart
   GoRoute(
     path: '/users/:id',
     builder: (c, s) => UserPage(id: s.pathParameters['id']!),
   )
   ```
2. **Query parameters** — optional filters, sort keys, search strings.
   ```dart
   final q = state.uri.queryParameters['q'];
   ```
3. **`extra`** — complex objects that can't serialize to a URL. Last resort: `extra` does NOT survive deep linking or app restarts. Never rely on it for state the app must recover.

## Shell routes (persistent UI)

For bottom-nav apps where the nav bar persists across tabs:

```dart
StatefulShellRoute.indexedStack(
  builder: (context, state, shell) => MainScaffold(shell: shell),
  branches: [
    StatefulShellBranch(routes: [
      GoRoute(path: AppRoutes.home.path, /* ... */),
    ]),
    StatefulShellBranch(routes: [
      GoRoute(path: AppRoutes.search.path, /* ... */),
    ]),
    StatefulShellBranch(routes: [
      GoRoute(path: AppRoutes.profile.path, /* ... */),
    ]),
  ],
)
```

Each branch preserves its own navigation stack. Switching tabs doesn't reset the inner stack — almost always desired.

## Auth redirects

Always use the router's `redirect` callback. Never gate navigation inside widgets.

`refreshListenable` is critical. Without it the redirect only re-evaluates on navigation events, not on auth state changes — a user who signs out in-app stays on a protected screen until they try to navigate.

## When to split (scaling beyond centralized)

Stick with the centralized `routes.dart` until it's noisy enough to slow reviews — in practice, past ~200 lines or ~15 routes. At that point, split by feature domain:

```
lib/app/router/
  app_router.dart
  routes.dart              # Top-level + shell structure, composes sub-files
  auth_routes.dart         # Login, signup, forgot password
  content_routes.dart      # Feed, item detail, search
  account_routes.dart      # Profile, settings, billing
```

Only go to per-feature route files (routes living inside each feature folder) if you have a very large app or features that need to ship as independent packages. The extra indirection costs readability; don't adopt it preemptively.

## Anti-patterns (do not do)

- **`Navigator.push(context, MaterialPageRoute(...))`** — bypasses the router, breaks deep linking and back/forward. Use `context.push` with a defined route.
- **Gating navigation in `initState` / `build`** — navigation inside widget lifecycle is a race. Put it in `redirect`.
- **Passing BLoCs through `extra`** — BLoCs are scoped via `BlocProvider`, not route arguments. Provide the BLoC at the route level if the destination needs it.
- **Hardcoded path strings at call sites** — `context.go('/users/42')` scattered across the app. Use `AppRoutes.*` constants for paths and names.
- **Deep nesting without a shell** — each level of nesting without a `ShellRoute` means losing the surrounding UI on navigation. Use shells deliberately.
