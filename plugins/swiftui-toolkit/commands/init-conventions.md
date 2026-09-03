---
description: Write a starter SwiftUI conventions block into this project's CLAUDE.md, resolving the project-conditional rules by reading its actual build settings. Only useful for a project that has not written its conventions down yet.
argument-hint: [path to the iOS project root, if not the repo root]
---

# init-conventions

**You probably do not need this.** If the project already states its conventions — a `CLAUDE.md` at
the root or beside a platform, a docs directory, ADRs — it is already in the state this produces,
and `dev-workflow:feature` reads them as they are. Say so and stop.

This is for a project starting from a blank page.

## What to do

1. Pick the file: `ios/CLAUDE.md` in a multi-platform repo, the root `CLAUDE.md` otherwise, or `$1`.
   If a `## SwiftUI conventions` section is already there, show a diff and let the user decide —
   never append a second one.

2. Take `${CLAUDE_PLUGIN_ROOT}/templates/claude-md-block.md` and resolve every `{{PLACEHOLDER}}`
   **by reading the project**. Never emit one, never guess one; ask if you cannot read it.

| Placeholder | Read it from |
|---|---|
| `{{APP_DIR}}` | The directory holding the `.xcodeproj`/`.xcworkspace` and app sources |
| `{{STRINGS_FILE}}` | The actual `*.xcstrings`. If strings are generated, say so and mark it never hand-edited |
| `{{ACTOR_ISOLATION_RULE}}` | `SWIFT_DEFAULT_ACTOR_ISOLATION` (`xcodebuild -showBuildSettings`, or the `.pbxproj`). `MainActor` → *"the project defaults to main-actor isolation; do not annotate `@MainActor` redundantly."* Unset → *"UI-touching types and `@Observable` stores are `@MainActor`."* **Opposite instructions — this is the whole reason this is a command and not a document to copy** |
| `{{BUILD_COMMAND}}` | The scheme from `xcodebuild -list`, never guessed. Include a clean variant |
| `{{TEST_COMMAND}}` | The test target, and a destination that exists (`xcrun simctl list devices available`) |
| `{{LINT_LINE}}` | If `.swiftlint.yml` exists, a line requiring zero warnings and errors. Otherwise empty |

3. **Do not state what the project has not decided** — deployment target, dark-mode support,
   whether SwiftData is used at all. An undecided question does not become decided by appearing in
   `CLAUDE.md`. Add a line only where the project has actually chosen.

4. Report every placeholder, the value you wrote, and where you read it. Those are the lines that
   would be wrong silently.

The technique skills — `api-style`, `design-tokens`, `logging`, `testing` — stay skills and are not
copied anywhere.
