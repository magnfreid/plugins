---
description: Seed this project's CLAUDE.md with an Android/Compose conventions block and copy the long-form notes into .claude/reference/, reading the project's real Gradle configuration rather than asserting defaults.
argument-hint: [path to the Android project root, if not the repo root]
---

# init-conventions

Write the Android and Compose conventions into **this project**, so they apply because they are in
an always-loaded file — not because a skill happened to trigger.

After seeding, the project owns the text. It is edited there, never here. There is deliberately no
runtime skill holding a second copy: two sources for one rule is how a toolkit default ends up
silently contradicting a decision the project already made.

## 1. Decide where it goes

- A repo with `ios/` and `android/` (or similar) → `android/CLAUDE.md`.
- A single-platform repo → the root `CLAUDE.md`.
- `$1`, if given, overrides the detection.

If a `## Android / Compose conventions` section already exists there, **do not append a second
one.** Show the user a diff of what would change and let them decide. Re-seeding over a project's
own edits is the one way this command can destroy work.

## 2. Read the project — do not assert

`${CLAUDE_PLUGIN_ROOT}/templates/claude-md-block.md` contains `{{PLACEHOLDER}}` markers. Every one
must be resolved from the project. **Never emit a placeholder, and never guess one.** If a value
cannot be read, ask rather than picking a default — a rule stated confidently and wrongly is worse
than a rule left out.

| Placeholder | Read it from |
|---|---|
| `{{SOURCE_ROOT}}` | The real source dir — `namespace` / `applicationId` in `app/build.gradle.kts`, and whether sources sit under `kotlin/` or the legacy `java/`. If it is `java/`, say so rather than describing a layout the repo does not have |
| `{{CI_NOTE}}` | Read `.github/workflows/*.yml` first — CI is the most reliable statement of what "passing" means. If CI exists, open with *"CI is authoritative; this chain mirrors `<workflow>`."* If the repo has its own script or Makefile target, name that instead |
| `{{VERIFY_CHAIN}}` | The tasks the project actually has. Include `spotlessCheck` / `ktlintCheck` / `detekt` **only if configured** — check the plugins block and `gradle/libs.versions.toml`. Then `assembleDebug`, `lint`, `testDebugUnitTest`, and `connectedDebugAndroidTest` |
| `{{REFERENCE_LIST}}` | The files you copy in step 3, as a comma-separated list of backticked names |

Things the template deliberately does **not** state, because they are project decisions this
command must not make: the networking stack, the persistence choice, `targetSdk`, and the Material 3
version. If the project has decided any of these, add a line saying so — and read it rather than
assuming, because asserting Retrofit at a project that uses Firebase Data Connect is exactly the
failure this command exists to avoid. If the project has not decided, leave it out.

## 3. Copy the reference notes

Copy `${CLAUDE_PLUGIN_ROOT}/templates/reference/*.md` into `.claude/reference/` in the project.
`architecture-notes.md` carries the reasoning behind the structural rules — why `data/` groups by
capability, why `designsystem/` and `ui/` stay apart, the growth path out of single-module. That
reasoning is what tells a future reader whether a departure is safe.

Never overwrite an existing file without showing the diff first.

## 4. Apply the rule budget

Before writing, cut. A rule earns its place only if breaking it makes two codebases structurally
different, or reaches for superseded API. *"There is a tidier way to write this"* does not qualify.

Prefer one mechanically-enforced rule to five prose ones. *"A warning introduced by the change
counts as a failure"* plus `./gradlew lint` is strictly stronger than a list of banned APIs, catches
next year's deprecations, and cannot go stale.

Structure is the cheapest conformity lever there is — a folder tree costs nothing to follow and
makes a feature recognisable across platforms. If this repo has an iOS or Flutter side too,
annotate the tree with the cross-platform equivalents; that is worth more than most prose.

## 5. Report

Tell the user: which file was seeded, every placeholder and the value you read for it (with where
you read it), which reference files landed, and anything you left out because the project had not
decided it. The placeholder values are the part worth checking — they are the ones that would be
wrong silently.
