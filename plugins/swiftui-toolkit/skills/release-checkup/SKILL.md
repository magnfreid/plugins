---
name: release-checkup
description: Audit a SwiftUI app before a release — six parallel auditors on Fable, merged into one report of work packages, each with a ship brief. Stops for approval, then starts one dev-workflow:ship session per approved package. Never edits the app itself and never merges. Invoked as /swiftui-toolkit:release-checkup.
argument-hint: [optional: a path to narrow the audit, or "since <tag>"]
disable-model-invocation: true
---

# Release checkup

```
scope → audit (6 × Fable, parallel) → merge → REPORT → [approve] → launch ship sessions
```

This finds and packages problems, and other sessions fix them. **It never edits the app, never
commits, and never merges.** The fixes are separate `dev-workflow:ship` sessions that open their own
pull requests.

## State

`.claude/workflow/release-checkup-<date>/` in the app repo, named for the day the run started. On
every invocation, look for an unfinished run in any earlier directory before creating one. Read `references/run-state.md` for the
files, the `state.json` shape and the resume rules. **A step counts as done only if its file
exists.** Never mark a step complete from memory.

On first run in a repo, append `.claude/workflow/` to `$(git rev-parse --git-common-dir)/info/exclude`
— in a linked worktree `.git` is a file, not a directory. The fix sessions stage
with `git add -A`, and an unexcluded workflow directory rides along into their commits.

## Step 1 — Scope

Read the root `CLAUDE.md` and the nearest ones. Find the app targets and scheme (`xcodebuild
-list`, never guessed from folder names), the deployment target, the platforms, the Swift settings,
test targets and the base branch (`git symbolic-ref refs/remotes/origin/HEAD`, after `git fetch`).

The argument narrows scope. A path limits the files, and `since <tag>` limits them to
`git diff --name-only <tag>...HEAD`. Exclude vendored and generated code (`Pods/`, `.build/`,
`DerivedData/`, `*.generated.swift`).

Ask Magnus only if the repo holds more than one app, and then in one question.

Write `scope.md`: repo root, base branch, scheme, targets, deployment target, platforms, Swift
settings, included paths, excluded paths, critical flows (from the README / `CLAUDE.md`, or "not
stated"), and any project-named skills from `CLAUDE.md`.

## Step 2 — Audit

Spawn six **release-auditor** agents **in one message** so they run in parallel, one per area key.
Give each: the area key, the absolute paths to `scope.md`, `references/audit-areas.md`,
`references/run-state.md`, and its `findings/<area>.md`. The `ui` spawn also gets "load
`swiftui-toolkit:hig`". Do not override the model: the agent pins Fable.

Transport failures are resumed by message, two attempts. An area that still fails is marked
`blocked` in `state.json`, and `report.md` lists it under Coverage. The report is still written, so
a missing area is visible, not silent.

## Step 3 — Merge and report

Read all findings.

**Dedupe.** Two findings are one when they share a file and an overlapping line range and describe
the same defect. Keep the clearer text, record both IDs, and take the higher severity.

**Group into work packages.** Findings that share files or one concern go together, sized so one PR
is reviewable (no package above roughly a dozen findings or more than one L). `later` findings are
not packaged unless Magnus asks.

**Estimate each package's file set** from its findings' "Files a fix touches". **Trap:** in an
Xcode project without folder-synchronized groups (no `PBXFileSystemSynchronizedRootGroup` in
`project.pbxproj`), any package that adds or removes a file also touches `project.pbxproj`, so
count it in the set.

**Chains.** Packages whose sets intersect run in sequence, must-fix first, then in report order.
Disjoint packages run in parallel.

**One PR or several.** Recommend one combined PR only when there are at most two packages and
neither is L. Then also include a combined brief. Otherwise recommend one PR per package.

Write `report.md` per `references/run-state.md`, then summarise in chat: the verdict line, one line
per package (ID, title, severity, size, wave), and the path to the report.

## Gate — approval

**Stop.** Nothing changes in the app before Magnus answers. He can approve all, approve some, edit a
package (change its scope or decisions, or merge or split packages) or reject. "Looks good"
approves everything. Silence approves nothing.

Apply edits to the package briefs yourself, since they are the orchestrator's own artifact.
Recompute the chains if packages were merged or split. Write `approval.md` (his reply verbatim and
the final package list) and one `packages/<WP-id>-<slug>.md` per approved package. When he approves
the combined-PR recommendation, write the combined brief as a single package file with one slug, in
place of the per-package files, and launch only that.

## Step 4 — Launch

Every fix run is its **own `dev-workflow:ship` session**, given the package brief as an
already-approved brief. Ship's models, review and PR behaviour apply unchanged. Fix runs open PRs
even in a repo whose `CLAUDE.md` names `feature`.

**Check first:** `claude --help` must list `--bg`, `--worktree`, `--name` and `--add-dir`. If it
does, run from the repo root, once per package in the current wave:

```
claude --bg --worktree <slug> --name "release: <title>" --add-dir "<abs run dir>" "/dev-workflow:ship <abs path to packages/WP-n-slug.md>"
```

Record the printed session id. The worktree is what lets parallel packages share no working tree.
`--add-dir` lets the session read a brief that lives outside its worktree.

**A chained package is `waiting` and is not launched until its predecessor's PR is merged.** Both
packages touch the same files, and `ship` branches from a fresh `origin/<base>`. Starting early puts
both changes on the same files from the same base, and one of them conflicts.

If the flags are missing, or a launch exits non-zero, print the same command for that package and
every other package in the current wave, and mark them `printed`. **Chained packages stay
`waiting` and their commands are not printed yet** — a command on screen is one that gets run
early. Re-invoking after the merge prints them.

Write `launches.md`: per package, the session id or command, and what it waits on. Tell Magnus
`claude agents` lists the sessions and `claude attach <id>` opens one that halted or is waiting on a
permission. Tell him to re-invoke `/swiftui-toolkit:release-checkup` after merges to launch the next
wave.

## Failure handling

Three buckets, as in `dev-workflow:ship`.

**Transport failure** — an agent killed by an API error, a stall, or a watchdog, having produced
nothing. Resume it by message. Two attempts, then halt.

**Judgment needed** — a halt recorded in `state.json`, or a launch that cannot proceed. **Halt**,
and Magnus decides.

**Everything else** — keep going.

Notify on any halt if a notification tool exists. **Never merge, never enable auto-merge, and never
edit app code to "help" a session.**
