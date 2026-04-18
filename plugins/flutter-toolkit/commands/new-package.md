---
name: new-package
description: Create a new Dart workspace package under packages/<name>/, scaffold its pubspec + analysis_options + barrel, and register it in the root pubspec.yaml as both a workspace member and a dependency.
argument-hint: "<package_name>"
---

# /new-package

Create a new workspace package under `packages/` and wire it into the root pubspec.

## Arguments

Package name in `$ARGUMENTS`. Must be a valid Dart package identifier: snake_case, lowercase, starts with a letter, may include digits and underscores. Reject names with hyphens, spaces, or uppercase.

## Before you act

1. Confirm `pubspec.yaml` exists at the project root.
2. Confirm `packages/<name>/` does not already exist.
3. Read the existing `pubspec.yaml` to see:
   - Whether a `workspace:` block exists.
   - The style used for workspace dependencies (path dependency vs versioned). Match what's already there.
4. Ask whether the new package is Flutter-adjacent (has widgets, pulls in `flutter`) or pure Dart. If unclear, default to Flutter — most packages in this monorepo are.

## Files to create

```
packages/<name>/
  pubspec.yaml
  analysis_options.yaml
  lib/
    <name>.dart
  test/
    .gitkeep
```

### `packages/<name>/pubspec.yaml` (Flutter variant)

```yaml
name: <name>
description: <name> package.
version: 0.0.1
publish_to: none
resolution: workspace

environment:
  sdk: ^3.9.0
  flutter: ">=3.24.0"

dependencies:
  flutter:
    sdk: flutter

dev_dependencies:
  flutter_lints: ^4.0.0
  flutter_test:
    sdk: flutter
```

### `packages/<name>/pubspec.yaml` (pure Dart variant)

```yaml
name: <name>
description: <name> package.
version: 0.0.1
publish_to: none
resolution: workspace

environment:
  sdk: ^3.9.0

dev_dependencies:
  lints: ^4.0.0
  test: ^1.25.0
```

### `packages/<name>/analysis_options.yaml`

Flutter variant:

```yaml
include: package:flutter_lints/flutter.yaml

analyzer:
  errors:
    public_member_api_docs: warning

linter:
  rules:
    public_member_api_docs: true
```

Pure Dart variant: replace `flutter_lints/flutter.yaml` with `lints/recommended.yaml`. Keep the `public_member_api_docs` rules either way — they are mandatory for any `packages/` member.

### `packages/<name>/lib/<name>.dart`

```dart
/// <Name> package.
library <name>;
```

## Edit root `pubspec.yaml`

Two changes:

1. Append `packages/<name>` to the `workspace:` list.
2. Add the new package to `dependencies:`, matching the existing style (path dependency preferred in a workspace):
   ```yaml
   <name>:
     path: packages/<name>
   ```

If there is no `workspace:` block yet, create one containing every existing `packages/*` directory plus the new one. Dart workspaces do not support globs, so each entry must be explicit.

## After you act

Report what was created and edited. Then remind the user to run:

```
./scripts/setup.sh
```

This runs `pub get` and resolves the workspace, making imports from the new package available.

## Do not

- Use version numbers for the workspace dependency (`<name>: ^0.0.1`) unless the existing pubspec already does. Path dependencies are the default.
- Scaffold any domain types (models, services) in the new package. Leave `lib/<name>.dart` as an empty barrel — the user fills it in.
- Copy the root's `analysis_options.yaml` verbatim. The package's analysis options must enable `public_member_api_docs`, which the root `lib/` does not.
