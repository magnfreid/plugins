---
description: Write a starter Android/Compose conventions block into this project's CLAUDE.md, resolving the project-conditional rules by reading its actual Gradle configuration. Only useful for a project that has not written its conventions down yet.
argument-hint: [path to the Android project root, if not the repo root]
---

# init-conventions

**You probably do not need this.** If the project already states its conventions — a `CLAUDE.md` at
the root or beside a platform, a docs directory, ADRs — it is already in the state this produces,
and `dev-workflow:feature` reads them as they are. Say so and stop.

This is for a project starting from a blank page.

## What to do

1. Pick the file: `android/CLAUDE.md` in a multi-platform repo, the root otherwise, or `$1`. If an
   `## Android / Compose conventions` section is already there, show a diff and let the user decide
   — never append a second one.

2. Take `${CLAUDE_PLUGIN_ROOT}/templates/claude-md-block.md` and resolve every `{{PLACEHOLDER}}`
   **by reading the project**. Never emit one, never guess one; ask if you cannot read it.

| Placeholder | Read it from |
|---|---|
| `{{SOURCE_ROOT}}` | `namespace` / `applicationId` in `app/build.gradle.kts`, and whether sources sit under `kotlin/` or the legacy `java/`. If it is `java/`, say so rather than describing a layout the repo does not have |
| `{{CI_NOTE}}` | `.github/workflows/*.yml` — CI is the most reliable statement of what "passing" means. If it exists, open with *"CI is authoritative; this chain mirrors `<workflow>`."* Prefer a repo script or Makefile target if there is one |
| `{{VERIFY_CHAIN}}` | The tasks the project actually has. `spotlessCheck` / `ktlintCheck` / `detekt` **only if configured** — check the plugins block and `gradle/libs.versions.toml`. Then `assembleDebug`, `lint`, `testDebugUnitTest`, `connectedDebugAndroidTest` |
| `{{REFERENCE_LIST}}` | `architecture-notes.md`, once you have copied it in step 3 |

3. Copy `${CLAUDE_PLUGIN_ROOT}/templates/reference/architecture-notes.md` into `.claude/reference/`
   — the reasoning behind the structural rules you just seeded. Show a diff before overwriting.

4. **Do not state what the project has not decided** — the networking stack, the persistence
   choice, `targetSdk`, the Material 3 version. Read them; asserting Retrofit at a project built on
   Firebase Data Connect is exactly the failure this command exists to avoid.

5. Report every placeholder, the value you wrote, and where you read it. Those are the lines that
   would be wrong silently.
