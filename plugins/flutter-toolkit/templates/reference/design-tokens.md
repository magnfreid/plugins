# Design tokens

*Project reference, seeded from `flutter-toolkit`. This project owns it — edit it here.*

Every visual value in the app comes from a token. Feature widgets read the theme; they never carry
hex literals, magic paddings, or `TextStyle`s built inline.

## Where tokens live

A dedicated `app_ui` workspace package, imported by `lib/` and by nothing else:

```
packages/app_ui/lib/
  colors/       AppColors — the seed and the ColorScheme built from it,
                plus any ThemeExtension carrying colours ColorScheme cannot hold
  typography/   the text theme
  themes/       AppTheme.lightTheme, AppTheme.darkTheme, and any scoped theme
```

Theme construction stays in `app_ui`. Do not move it into `lib/`, and do not build a second theme
inline in a feature.

## ColorScheme or ThemeExtension

**`ColorScheme` first.** Build it with `ColorScheme.fromSeed` and use the semantic roles —
`primary`, `surface`, `onSurfaceVariant`, `outline`. A value that maps onto a Material role belongs
there, because every Material widget already reads it.

**`ThemeExtension` when the role does not exist.** Brand surfaces, a warm off-white that is not
`surface`, a bubble colour, a custom elevation ramp. Define it as a typed extension with `copyWith`
and `lerp`, register it on the theme, and read it via `Theme.of(context).extension<T>()!`.

Never reach for a `ThemeExtension` because the `ColorScheme` role "isn't quite right" — adjust the
seed or the role. Extensions are for values Material has no concept of.

## Adding a token

When a design introduces a value nothing covers, **adding the token is part of that work.** The
sequence is: name it semantically, add it to `app_ui`, then use it. Never inline the literal with a
plan to tokenize later — the literal is what ships, and the next screen copies it.

Name for role, not appearance: `interviewSurface`, not `warmOffWhite`; `bubbleUser`, not `sageGreen`.
A design that renames the colour then costs one token edit rather than a find-and-replace across
features.

## Scoping a redesign to one screen

A redesign usually lands one screen at a time, and changing the global theme to suit the first one
restyles the eight screens nobody designed. Scope it instead:

```dart
// packages/app_ui/lib/themes/app_theme.dart
/// Layers the redesign's surface and type scale onto [base].
///
/// Scoped deliberately: only the screens that have adopted the redesign wrap
/// themselves in it. When the rest follow, move this into [_base] and delete
/// the per-screen wraps.
static ThemeData warmTheme(ThemeData base) => base.copyWith(/* ... */);
```

```dart
// lib/interview/view/interview_page.dart
Theme(
  data: AppTheme.warmTheme(Theme.of(context)),
  child: const InterviewView(),
)
```

Two things make this work rather than becoming permanent sprawl: the scoped theme lives in `app_ui`
with the rest of the theming, and its doc comment states the exit condition. Write that exit
condition when you create it — a scoped theme with no stated end is just a fork.

## Rules

- **No hex literals, no `Color(0xFF...)`, no inline `TextStyle` in feature widgets.** If you are
  typing a colour inside `lib/<feature>/`, a token is missing.
- **No magic spacing numbers** where a spacing token exists.
- Read typography from the text theme (`Theme.of(context).textTheme.bodyLarge`), not by constructing
  `TextStyle` at the call site.
- A screen that opts out of a global theme decision must say why in a comment. Silent divergence is
  how two design systems end up in one app.
- Implementing a design handoff? Load `dev-workflow:design-handoff` first — it covers what to verify
  in the handoff before any of this matters.
