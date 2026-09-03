---
description: Write a starter Flutter conventions block into this project's CLAUDE.md, resolving the project-conditional rules by reading its actual pubspec and tooling. Only useful for a project that has not written its conventions down yet.
argument-hint: [path to the Flutter project root, if not the repo root]
---

# init-conventions

**You probably do not need this.** If the project already states its conventions — a `CLAUDE.md` at
the root or beside a platform, a docs directory, ADRs — it is already in the state this produces,
and `dev-workflow:feature` reads them as they are. Say so and stop.

This is for a project starting from a blank page.

## What to do

1. Pick the file: the Flutter app's own `CLAUDE.md` in a multi-platform repo, the root otherwise,
   or `$1`. If a `## Flutter conventions` section is already there, show a diff and let the user
   decide — never append a second one.

2. Take `${CLAUDE_PLUGIN_ROOT}/templates/claude-md-block.md` and resolve every `{{PLACEHOLDER}}`
   **by reading the project**. Never emit one, never guess one; ask if you cannot read it.

| Placeholder | Read it from |
|---|---|
| `{{WORKSPACE_NOTE}}` | The root `pubspec.yaml`. A `workspace:` key → describe the workspace wiring (explicit member list, `resolution: workspace`). Path dependencies → describe *those*. Do not describe a workspace the repo does not have |
| `{{FVM_NOTE}}` | Whether `.fvmrc` / `.fvm/` exists. If so, require `fvm flutter …`; if not, drop the note and use bare commands below |
| `{{VERIFY_CHAIN}}` | The real chain: `build_runner` only if the repo has codegen inputs (search for `@freezed` / `@JsonSerializable`), then `analyze`, `format --set-exit-if-changed`, `test`. Prefix `fvm ` only if FVM is present. If `scripts/verify.sh` exists, use that — one command that cannot drift beats four that can |
| `{{WORKSPACE_TEST_WARNING}}` | Only if `packages/` has tests: the root run does not descend into members, so a repo with its domain logic there reports green having run a fraction of its suite. Otherwise empty |

3. **Do not state what the project has not decided** — the HTTP client, the backend, the Dart SDK
   floor (dot shorthands need 3.10+; check `environment:`). An undecided question does not become
   decided by appearing in `CLAUDE.md`.

4. Report every placeholder, the value you wrote, and where you read it. Those are the lines that
   would be wrong silently.

The technique skills — `bloc`, `dio`, `routing`, `l10n`, `design-tokens`, `testing` — stay skills
and are not copied anywhere.
