# Run state — release-checkup

Everything the orchestrator and the auditors share. **A step counts as done only if its file
exists.**

## Directory

`.claude/workflow/release-checkup-<YYYY-MM-DD>/` in the app repo. The date names a new run and
nothing else: it is the day the run started, not the day of any later invocation. On every
invocation, first scan all `.claude/workflow/release-checkup-*` directories for an unfinished run
and resume it (see Resume rules). A run is finished when every package is `merged`, `rejected` or
`printed`, or `launch` is done with nothing waiting. Only when none is unfinished, create a new
directory for today's date, with the suffix `-2`, `-3`, and so on if that name is taken.

## Files

| File | Written by | Step it proves done |
|---|---|---|
| `state.json` | orchestrator | — |
| `scope.md` | orchestrator | `scope` |
| `findings/<area>.md` | release-auditor, one per area | `audit` (all six present) |
| `report.md` | orchestrator | `report` |
| `approval.md` | orchestrator, recording Magnus's reply verbatim plus the resulting package list | `approval` |
| `packages/<WP-id>-<slug>.md` | orchestrator: the final ship brief per approved package (written at approval) | — |
| `launches.md` | orchestrator: per package, the session id or the printed command, and what it waits on | `launch` |

Area keys, in this order: `correctness`, `architecture`, `code-health`, `security`, `ui`, `release`.
Finding ID prefixes: `COR`, `ARC`, `HLT`, `SEC`, `UI`, `REL`.

## state.json

```json
{
  "run": "release-checkup-2026-11-09",
  "created": "2026-11-09T10:14:00+01:00",
  "repoRoot": "/Users/magnfreid/dev/myapp",
  "baseBranch": "main",
  "scheme": "MyApp",
  "deploymentTarget": "iOS 17.0",
  "scope": "whole app",
  "steps": {
    "scope": "done",
    "audit": "done",
    "report": "done",
    "approval": "pending",
    "launch": "pending"
  },
  "areas": {
    "correctness": "done", "architecture": "done", "code-health": "done",
    "security": "done", "ui": "blocked", "release": "done"
  },
  "packages": {
    "WP-1": {
      "slug": "release-crash-hardening",
      "status": "launched",
      "after": [],
      "session": "a1b2c3",
      "pr": null
    }
  },
  "halt": null
}
```

Package `status` values: `proposed` → `approved` | `rejected` → `waiting` (blocked on `after`) →
`launched` | `printed` → `pr-open` → `merged`. Step status values: `pending`, `done`, `blocked`,
the same as ship.

## Findings file

`findings/<area>.md`, one block per finding:

```markdown
### COR-3 — `Sources/Checkout/CartStore.swift:88`
**What:** `try!` on decoding the cached cart.
**Why it matters for release:** a cart cached by the previous version that fails to decode crashes the app on launch, every launch, until reinstall.
**Severity:** must-fix
**Size:** S
**Files a fix touches:** `Sources/Checkout/CartStore.swift`
```

A file with nothing to report has the line `No findings.` and then its `## Not checked` section. A file ends with an
`## Not checked` section listing anything the area asks for that the auditor could not check, and
why (for example "build warnings: no scheme builds without signing"). That section is required
even when empty, and then it reads `Nothing.`

Severity:
- **must-fix**: crash, data loss, security or privacy exposure, a likely App Review rejection, a
  broken core flow, or a licence violation.
- **should-fix**: a user-visible defect off the critical path, an accessibility failure, an
  unapproved HIG deviation, or noticeable slowness.
- **later**: code health with no user-visible effect.

Size: **S** is one file and a few lines. **M** is several files with one concern. **L** is
cross-cutting, or needs a design decision.

## report.md

Sections, in order:

1. `## Summary` — counts by severity and by area, plus a one-line verdict ("N must-fix items stand
   between this build and release").
2. `## Work packages` — must-fix packages first. Per package: `### WP-n — <title>`, then severity
   (the highest of its findings), size, the finding IDs it covers, the estimated files it touches,
   `Runs with:` (packages it can run in parallel with), `Runs after:` (its predecessor in a chain,
   or `—`), and the full ship brief in a fenced `markdown` block.
3. `## Recommendation` — one PR or several, the launch waves (wave 1 is every package with no
   predecessor; wave n+1 is the packages whose predecessors are in wave n), and the order.
4. `## Not packaged` — `later` findings, one line each with their ID. Findings merged as duplicates
   are listed as `COR-2 = UI-5`.
5. `## Coverage` — every auditor's `Not checked` items, plus any area that failed to run.

## Package brief

This is what ship receives:

```markdown
# <Package title>

Approved: swiftui-toolkit:release-checkup, <YYYY-MM-DD>
Slug: <package slug>
Base branch: <base branch>

## Objective
<what is being fixed and why it blocks or affects the release; two or three sentences>

## Decisions taken
- <each finding in the package: ID, file:line, the fix direction the auditor gave>
- <any decision Magnus made at approval>

## Project-named skills
- <each skill `scope.md` recorded from `CLAUDE.md`, and the kind of change it covers — or "none">

## Out of scope
- <the other packages' findings that touch nearby code>
- Anything not listed above.
```

Package slug: `release-<kebab-case of the title>`, at most 40 characters, unique within the run.

## Resume rules

Re-invoking the skill in a repo with an unfinished run directory, whatever its date, resumes rather
than restarts. With more than one unfinished run, ask which to resume.

1. When `halt` is set, show the reason and ask whether to retry, skip or abandon.
2. Trust files over status. An area is done when its findings file exists.
3. When resuming at `audit`, spawn only the areas whose file is missing.
4. When resuming after `launch`, for each package with a `session` or a printed command, look up
   its PR with `gh pr list --state all --head feature/<slug> --json url,state` and then
   `--head fix/<slug>`. Record `pr` and move the status to `pr-open` or `merged`.
5. Launch every `waiting` package whose predecessors are all `merged` — or, when the launch
   flags are missing, print its command now and mark it `printed`.
6. Report what is still waiting, and on what.

## Multiple runs

One directory per run; several may coexist. If more than one is unfinished, list them and ask which
to resume rather than guessing.
