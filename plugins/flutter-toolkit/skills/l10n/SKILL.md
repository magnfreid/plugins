---
name: l10n
description: How to work with Flutter's built-in gen-l10n — ARB file structure, placeholders, plurals and selects, adding a locale, wiring the delegate, and regenerating after an edit. Use when adding or changing a user-facing string in a Flutter project that uses gen-l10n.
---

# Localizing with gen-l10n

How to add and change strings once a project is localizing through gen-l10n. Which locales a project supports, and which is the default, are its own decisions — read them from its `l10n.yaml` and ARB files rather than assuming.

**Technique, not choice.** This is how to work with Flutter's built-in gen-l10n once the project has decided to
use it. Whether to use it at all, where the files live, and what things are called are the
project's decisions — its `CLAUDE.md` and the patterns already in the code win over anything
here, and they win without discussion. Nothing in this file is a reason to restructure a repo.


## Setup assumptions

This assumes gen-l10n is already wired. **Read the project's `l10n.yaml` for the real paths,
template file, and output class** — do not assume the layout below.

Which locales a project supports, and which one is the template, are its decisions. The example
uses `en` as the template and one translation alongside it; substitute whatever the repo has.

- `flutter_localizations` from SDK + `intl` as dependencies.
- `l10n.yaml` at project root — the authority for everything that follows.
- ARB files, conventionally in `lib/l10n/`:
  - `app_<template>.arb` — source of truth, must contain every key.
  - `app_<locale>.arb` — one per additional locale.
- `MaterialApp` wired with:
  ```dart
  localizationsDelegates: AppLocalizations.localizationsDelegates,
  supportedLocales: AppLocalizations.supportedLocales,
  ```

If any of this is missing, set it up before adding strings.

## ARB file anatomy

Each key pairs with an optional `@key` metadata entry describing placeholders, plurals, or context.

```json
{
  "@@locale": "en",
  "loginTitle": "Sign in",
  "@loginTitle": {
    "description": "Title on the login screen"
  },
  "welcomeUser": "Welcome, {name}",
  "@welcomeUser": {
    "description": "Greeting on home screen",
    "placeholders": {
      "name": {
        "type": "String",
        "example": "Magnus"
      }
    }
  },
  "unreadMessages": "{count, plural, =0{No messages} =1{1 message} other{{count} messages}}",
  "@unreadMessages": {
    "description": "Badge text for unread messages",
    "placeholders": {
      "count": {
        "type": "int"
      }
    }
  }
}
```

Rules:

- `app_en.arb` MUST contain the `@@locale` header and `@key` metadata for every keyed placeholder. Other locales (`app_sv.arb`) only need translated values — they inherit metadata from English.
- Every key in `app_en.arb` must exist in every other locale file. Missing keys cause runtime fallbacks to English.
- Always type placeholders (`String`, `int`, `num`, `DateTime`). Untyped placeholders generate `Object` which is never what you want.

## Codegen (critical — do not skip)

After creating or modifying ANY `.arb` file, run:

```
fvm flutter gen-l10n
```

This regenerates `AppLocalizations` under `.dart_tool/flutter_gen/`. Without it, new keys don't exist at compile time. Do not leave the user with a broken build.

No `build_runner`, no `intl_utils`. The Flutter-native `gen-l10n` is the only tool.

## Using strings in widgets

```dart
final l10n = AppLocalizations.of(context)!;

Text(l10n.loginTitle);
Text(l10n.welcomeUser('Magnus'));
Text(l10n.unreadMessages(count));
```

Bind once at the top of `build()` rather than chaining `AppLocalizations.of(context)!.x` throughout the tree.

## Adding a new locale

1. Add the new ARB file, e.g. `app_de.arb`, mirroring all keys from `app_en.arb`.
2. Run `fvm flutter gen-l10n`.
3. The new locale is picked up automatically via `AppLocalizations.supportedLocales` — no extra wiring.

## Anti-patterns (do not do)

- **Hardcoded user-facing strings** — every visible string goes through ARB. Only untranslatable strings (URLs, class names, file paths) can be literal.
- **String concatenation for dynamic content** — use placeholders. `'Welcome, ' + name` breaks grammar and word order in many languages.
- **Plurals branched in Dart code** — use ARB `plural` syntax. Dart-side branching on count produces grammatically wrong output in Slavic and other complex-plural languages.
- **Chaining `AppLocalizations.of(context)` without null-checking** — it can be null during early bootstrap. Either `!` and trust the wiring, or handle null explicitly.
