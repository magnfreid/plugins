---
description: Seed this project's CLAUDE.md with a SwiftUI conventions block and copy the long-form blueprints into .claude/reference/, reading the project's real build settings rather than asserting defaults.
argument-hint: [path to the iOS project root, if not the repo root]
---

# init-conventions

Write the SwiftUI conventions into **this project**, so they apply because they are in an
always-loaded file — not because a skill happened to trigger.

After seeding, the project owns the text. It is edited there, never here. There is deliberately no
runtime skill holding a second copy: two sources for one rule is how a toolkit default ends up
silently contradicting a decision the project already made.

## 1. Decide where it goes

- A repo with `ios/` and `android/` (or similar) → `ios/CLAUDE.md`.
- A single-platform repo → the root `CLAUDE.md`.
- `$1`, if given, overrides the detection.

If a `## SwiftUI conventions` section already exists there, **do not append a second one.** Show
the user a diff of what would change and let them decide. Re-seeding over a project's own edits is
the one way this command can destroy work.

## 2. Read the project — do not assert

`${CLAUDE_PLUGIN_ROOT}/templates/claude-md-block.md` contains `{{PLACEHOLDER}}` markers. Every one
must be resolved from the project. **Never emit a placeholder, and never guess one.** If a value
cannot be read, ask rather than picking a default — a rule stated confidently and wrongly is worse
than a rule left out.

| Placeholder | Read it from |
|---|---|
| `{{APP_DIR}}` | The directory holding the `.xcodeproj`/`.xcworkspace` and app sources |
| `{{STRINGS_FILE}}` | The actual string catalog — find `*.xcstrings`. If strings are generated into a build dir, say so and mark the file as never hand-edited |
| `{{ACTOR_ISOLATION_RULE}}` | `SWIFT_DEFAULT_ACTOR_ISOLATION` in the build settings (`xcodebuild -showBuildSettings`, or the `.pbxproj`). If it is `MainActor`, the rule is *"the project defaults to main-actor isolation; do not annotate `@MainActor` redundantly."* If it is not set, the rule is *"UI-touching types and `@Observable` stores are `@MainActor`."* **These are opposite instructions. Getting it wrong plants a wrong rule in an always-loaded file** |
| `{{BUILD_COMMAND}}` | Discover the scheme with `xcodebuild -list` — never guess it. Include a clean build variant |
| `{{TEST_COMMAND}}` | The test target and a destination that actually exists (`xcrun simctl list devices available`) |
| `{{LINT_LINE}}` | If `.swiftlint.yml` exists: *" SwiftLint must report zero warnings and zero errors before committing."* Otherwise empty |
| `{{REFERENCE_LIST}}` | The files you copy in step 3, as a comma-separated list of backticked names |

Things the template deliberately does **not** state, because they are project decisions this
command must not make: the deployment target, whether dark mode is supported, and whether SwiftData
is used at all. If the project has decided any of these, add a line saying so. If it has not, leave
it out — an undecided question does not become decided by appearing in `CLAUDE.md`.

## 3. Copy the blueprints

Copy `${CLAUDE_PLUGIN_ROOT}/templates/reference/*.md` into `.claude/reference/` in the project.
These are long-form patterns — API style, design tokens, logging, testing — too long for
`CLAUDE.md` and too specific to reconstruct from memory.

Skip any file the project would not use, and say which you skipped. Never overwrite an existing
file without showing the diff first.

## 4. Apply the rule budget

Before writing, cut. A rule earns its place only if breaking it makes two codebases structurally
different, or reaches for superseded API. *"There is a tidier way to write this"* does not qualify.

Prefer one mechanically-enforced rule to five prose ones. *"A warning introduced by the change
counts as a failure"* is strictly stronger than a list of banned APIs, catches next year's
deprecations, and cannot go stale. Hunt for more of these — a lint rule or a compiler setting beats
a paragraph every time.

## 5. Report

Tell the user: which file was seeded, every placeholder and the value you read for it (with where
you read it), which reference files landed, and anything you left out because the project had not
decided it. The placeholder values are the part worth checking — they are the ones that would be
wrong silently.
