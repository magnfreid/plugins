---
description: Seed this project's CLAUDE.md with a Flutter conventions block and copy the long-form blueprints into .claude/reference/, reading the project's real pubspec and tooling rather than asserting defaults.
argument-hint: [path to the Flutter project root, if not the repo root]
---

# init-conventions

Write the Flutter conventions into **this project**, so they apply because they are in an
always-loaded file — not because a skill happened to trigger.

After seeding, the project owns the text. It is edited there, never here. There is deliberately no
runtime skill holding a second copy: two sources for one rule is how a toolkit default ends up
silently contradicting a decision the project already made.

## 0. Check whether it is wanted at all

This command is optional. If the project already states its conventions — in a `CLAUDE.md` at the
root or beside a platform, in a docs directory, in ADRs — then it is already in the state this
command produces, and the workflow reads them as they are.

Say so and stop, unless the user explicitly wants the block seeded anyway. Overwriting a project's
own writing with a generated default is the worst outcome available here.

## 1. Decide where it goes

- A multi-platform repo → the Flutter app's own `CLAUDE.md`.
- A single-platform repo → the root `CLAUDE.md`.
- `$1`, if given, overrides the detection.

If a `## Flutter conventions` section already exists there, **do not append a second one.** Show the
user a diff of what would change and let them decide. Re-seeding over a project's own edits is the
one way this command can destroy work.

## 2. Read the project — do not assert

`${CLAUDE_PLUGIN_ROOT}/templates/claude-md-block.md` contains `{{PLACEHOLDER}}` markers. Every one
must be resolved from the project. **Never emit a placeholder, and never guess one.** If a value
cannot be read, ask rather than picking a default — a rule stated confidently and wrongly is worse
than a rule left out.

| Placeholder | Read it from |
|---|---|
| `{{WORKSPACE_NOTE}}` | The root `pubspec.yaml`. If it has a `workspace:` key, state that members are wired as a Dart workspace, that the list is explicit (globs are unsupported), and that each member sets `resolution: workspace`. If it uses path dependencies instead, describe *that* — do not describe a workspace the repo does not have |
| `{{FVM_NOTE}}` | Whether `.fvmrc` / `.fvm/` exists. If it does: *"Always `fvm flutter …` / `fvm dart …`, never bare `flutter`."* If not, drop the note and use bare commands in the chain |
| `{{VERIFY_CHAIN}}` | The real chain, in order: `build_runner` only if the repo has codegen inputs (search for `@freezed` / `@JsonSerializable`), then `analyze`, `format --set-exit-if-changed`, `test`. Prefix with `fvm ` only if FVM is present. If `scripts/verify.sh` exists, use that instead — one command that cannot drift beats four that can |
| `{{WORKSPACE_TEST_WARNING}}` | Only if the repo has `packages/` with tests: *"The root test run does not descend into workspace members. A repo keeping its domain logic in `packages/` will report green having run a fraction of its suite — iterate the packages explicitly."* Otherwise empty |
| `{{REFERENCE_LIST}}` | The files you copy in step 3, as a comma-separated list of backticked names |

Things the template deliberately does **not** state, because they are project decisions this
command must not make: the HTTP client, the backend, and the Dart SDK floor (dot-shorthand syntax
needs Dart 3.10+ — check `environment:` before recommending it). If the project has decided any of
these, add a line saying so. If it has not, leave it out.

## 3. Copy the blueprints

Copy `${CLAUDE_PLUGIN_ROOT}/templates/reference/*.md` into `.claude/reference/` in the project —
`bloc`, `dio`, `routing`, `l10n`, `design-tokens`, `testing`. These are long-form patterns too long
for `CLAUDE.md` and too specific to reconstruct from memory.

**Skip what the project does not use.** A repo with no HTTP layer should not carry `dio.md`; a repo
that is not localized should not carry `l10n.md`. Say which you skipped and why. Never overwrite an
existing file without showing the diff first.

## 4. Apply the rule budget

Before writing, cut. A rule earns its place only if breaking it makes two codebases structurally
different, or reaches for superseded API. *"There is a tidier way to write this"* does not qualify.

Prefer one mechanically-enforced rule to five prose ones. A lint rule in `analysis_options.yaml`
beats a paragraph every time, and `dart format --set-exit-if-changed` settles every formatting
argument at once.

## 5. Report

Tell the user: which file was seeded, every placeholder and the value you read for it (with where
you read it), which reference files landed and which you skipped, and anything you left out because
the project had not decided it. The placeholder values are the part worth checking — they are the
ones that would be wrong silently.
