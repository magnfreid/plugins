# Workflow state

`.claude/workflow/<slug>/state.json`:

```json
{
  "slug": "order-history-pagination",
  "created": "2026-09-09T10:14:00+02:00",
  "stack": "flutter",
  "implementer": "sonnet",
  "repoRoot": "/Users/magnfreid/dev/myapp",
  "baseBranch": "main",
  "branch": "feature/order-history-pagination",
  "verification": [
    "fvm dart run build_runner build --delete-conflicting-outputs",
    "fvm dart analyze",
    "fvm flutter test"
  ],
  "steps": {
    "clarify":   "done",
    "plan":      "done",
    "approved":  "done",
    "implement": "done",
    "review":    "blocked",
    "fix":       "pending",
    "commit":    "pending",
    "handoff":   "pending"
  },
  "halt": {
    "step": "review",
    "reason": "reviewer returned ESCALATE — pagination cursor belongs in the repository, not the BLoC",
    "at": "2026-09-09T10:52:00+02:00"
  }
}
```

Status values: `pending`, `done`, `blocked`. `halt` is present only when a step stopped, and is
cleared when that step later succeeds.

`implementer` is the model confirmed at the gate.

There is no `pr` field and no review level. The workflow does not open a pull request, and there is
one review lens — if a change needs a harder look, Magnus asks for it at the handoff.

## Resume rules

Re-invoking the skill in a repo with an existing workflow directory resumes rather than restarts.

1. Read `state.json`. If `halt` is set, show the user the reason first and ask whether to retry
   that step, skip it, or abandon the run. Do not silently retry — the halt was a decision, not an
   accident. The single exception is rule 6.
2. Otherwise find the first step that is not `done` and start there.
3. **Trust files, not the status field.** If a step is marked `done` but its file is missing, it is
   not done. If the file exists but the status says pending, the file wins. The status field is a
   convenience; the artifacts are the truth.
4. Before resuming at `implement` or later, verify the branch in `state.json` exists and is checked
   out. If the user has moved on, stop and ask rather than committing to the wrong branch.
5. `approved` is never inferred. If it is not `done`, the gate has not been passed, and the run
   goes back to the gate — even if `plan.md` exists.
6. A halt whose reason was a **transport failure** — an agent killed by an API error, a stall, or a
   watchdog, having produced nothing — is the one case that may be retried without asking, up to
   two attempts. Record each attempt in `halt`. Every other halt goes back to the user, because
   every other halt is something an agent decided rather than something that happened to it.

`commit` has no artifact file of its own. It is done when the branch's HEAD is a commit containing
the work — check the git state, not the status field, and never commit twice.

## Multiple runs

One directory per slug; several may coexist. If more than one has incomplete steps, list them and
ask which to resume rather than guessing. Finished runs are worth keeping — `plan.md` next to a
merged PR is the best record of why the code looks the way it does.
