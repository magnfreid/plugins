# Workflow state

`.claude/workflow/<slug>/state.json`:

```json
{
  "slug": "order-history-pagination",
  "created": "2026-08-22T10:14:00+02:00",
  "stack": "flutter",
  "repoRoot": "/Users/magnfreid/dev/myapp",
  "baseBranch": "main",
  "branch": "feature/order-history-pagination",
  "pr": 142,
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
    "draft_pr":  "done",
    "review":    "blocked",
    "fix":       "pending",
    "ready":     "pending"
  },
  "halt": {
    "step": "review",
    "reason": "reviewer returned ESCALATE — pagination cursor belongs in the repository, not the BLoC",
    "at": "2026-08-22T10:52:00+02:00"
  }
}
```

Status values: `pending`, `done`, `blocked`. `halt` is present only when a step stopped, and is
cleared when that step later succeeds.

## Resume rules

Re-invoking the skill in a repo with an existing workflow directory resumes rather than restarts.

1. Read `state.json`. If `halt` is set, show the user the reason first and ask whether to retry
   that step, skip it, or abandon the run. Do not silently retry — the halt was deliberate.
2. Otherwise find the first step that is not `done` and start there.
3. **Trust files, not the status field.** If a step is marked `done` but its file is missing, it is
   not done. If the file exists but the status says pending, the file wins. The status field is a
   convenience; the artifacts are the truth.
4. Before resuming at `implement` or later, verify the branch in `state.json` exists and is checked
   out. If the user has moved on, stop and ask rather than committing to the wrong branch.
5. `approved` is never inferred. If it is not `done`, the gate has not been passed, and the run
   goes back to the gate — even if `plan.md` exists.

## Multiple runs

One directory per slug; several may coexist. If more than one has incomplete steps, list them and
ask which to resume rather than guessing. Finished runs are worth keeping — `plan.md` next to a
merged PR is the best record of why the code looks the way it does.
