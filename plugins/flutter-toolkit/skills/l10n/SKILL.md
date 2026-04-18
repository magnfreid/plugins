---
name: l10n
description: Flutter localization with gen-l10n + ARB files. Trigger on any translation or internationalization work — "add a translation", "new string for the UI", ".arb", "add Swedish/English", placeholders, plurals, supporting a new locale, or running gen-l10n after editing arb files.
---

# l10n

Conventions for localization in this Flutter stack: Flutter's built-in `gen-l10n` (no `build_runner`, no `intl_utils`), ARB files per locale, English as the default, Swedish as the second supported locale.

## Setup assumptions

The project already has:

- `flutter_localizations` from SDK + `intl` as dependencies.
- `l10n.yaml` at project root.
- ARB files in `lib/l10n/`:
  - `app_en.arb` — source of truth, must contain every key.
  - `app_sv.arb` — Swedish translations.
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
