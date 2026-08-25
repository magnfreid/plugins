# compose-toolkit

Claude Code plugin for Android development with Jetpack Compose. Encodes opinionated defaults around
state management, project structure, and testing so Claude produces code that matches how you'd
actually ship it.

Deliberately **conventional**: where Google states a recommendation, this toolkit follows it rather
than inventing a house style. Where Google states nothing — project structure, error mapping,
what must be tested — this toolkit decides.

## Skills

| Skill | Triggers on |
| --- | --- |
| [`conventions`](./skills/conventions/SKILL.md) | The architectural defaults themselves — load before planning or implementing |

Planned: `state`, `composition`, `networking`, `design-tokens`, `testing`, `gradle`, `l10n`,
`logging`, and the `compose-architect` / `compose-implementer` / `compose-test-writer` /
`compose-refactor` agents.

## Companion: Google's `android-skills`

This toolkit assumes Google's official skills are installed alongside it:

```
/plugin marketplace add android/skills
/plugin install android-skills@android-skills
```

The two do different jobs and are written not to overlap. `android-skills` targets *"use cases and
workflows where evaluations show LLMs underperform"* and explicitly excludes basic Compose practice,
architecture, and project structure — so it answers **how to execute correctly against current
APIs**. This toolkit answers **which choice we make**.

`conventions` delegates these outright rather than duplicating them:

| Topic | Skill |
| --- | --- |
| Navigation 3 mechanics, recipes, nav2 migration | `android-skills:navigation-3` |
| Test library and harness setup | `android-skills:testing-setup` |
| AGP 9 upgrades, KSP/KAPT, BuildConfig | `android-skills:agp-9-upgrade` |
| Edge-to-edge layout | `android-skills:edge-to-edge` |
| Adaptive layouts, window size classes | `android-skills:adaptive` |

## Assumptions

- Single-module app, Kotlin, Jetpack Compose, `compileSdk` current
- MVVM as Google defines it — one `uiState: StateFlow<XUiState>` per screen, actions as functions
- Navigation 3, Hilt, Retrofit + kotlinx.serialization, Room + DataStore
- Material 3 **stable** — not the Expressive alphas
- Android-only; no Compose Multiplatform

If your project diverges from these, the generated code may not fit.

## Version

See [`.claude-plugin/plugin.json`](./.claude-plugin/plugin.json) — currently `0.1.0`.
