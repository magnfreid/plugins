# Workflow state — ship

Same directory and the same files as `feature`. Two differences in the state machine: there is no
`approved` step, and the run ends at `pr` rather than `handoff`.

`.claude/workflow/<slug>/state.json`:

```json
{
  "slug": "order-history-pagination",
  "created": "2026-09-22T10:14:00+02:00",
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
  "slowSuite": {
    "name": "integration tests (integration_test)",
    "commands": ["fvm flutter test integration_test"]
  },
  "fullRun": {
    "sha": "9c4e1f0b2a7d3e8f6c5b4a3d2e1f0a9b8c7d6e5f",
    "result": "passed",
    "at": "2026-09-10T16:03:00+02:00",
    "merged": {
      "sha": "4d8a1c7e5b2f9a3c6e0d1b7f8a4c2e9d5b3f1a60",
      "url": "https://github.com/magnfreid/myapp/pull/42",
      "at": "2026-09-10T16:20:00+02:00"
    }
  },
  "pr": "https://github.com/magnfreid/myapp/pull/42",
  "steps": {
    "clarify":   "done",
    "plan":      "done",
    "implement": "done",
    "review":    "blocked",
    "fix":       "pending",
    "commit":    "pending",
    "pr":        "pending"
  },
  "halt": {
    "step": "review",
    "reason": "reviewer returned ESCALATE — pagination cursor belongs in the repository, not the BLoC",
    "at": "2026-09-22T10:52:00+02:00"
  }
}
```

Status values: `pending`, `done`, `blocked`. `halt` is present only when a step stopped, and is
cleared when that step later succeeds.

`implementer` is chosen by the orchestrator from the finished plan, not confirmed by Magnus —
there is no gate at which to confirm it.

`briefSource` is optional and absent on a normal run. When the run started from a pre-approved
brief, it holds the text after `Approved:`. With a pre-approved brief, `clarify` is done as soon as
`brief.md` exists, the same rule as any other step.

`verification` is the fast loop and `slowSuite` the slow suite, both from
`../feature/references/stack-detection.md`. `slowSuite` is absent when the stack has none. Its
`name` is how the report and the PR body's Verification section refer to it.

`fullRun` is absent until the final run has happened, and records the latest one: the HEAD it ran
on, `passed` or `failed`, and when. **It counts only while `sha` is the branch's current HEAD.** A
commit after it, whether a revision or a fix, leaves it in place as history and makes it stale.
Never write `passed` for a run that did not finish green. A merge is never made without a
`passed` `fullRun` on HEAD. `fullRun.merged` is present only once the PR has been merged: the merge
commit, the PR URL, and when. A merged run is finished.

`pr` holds the pull request URL once it exists, and is absent until then. It is the one field that
proves the run finished: a `pr` step marked `done` with no URL is not done.

There is no review-level field. This flow always reviews at `high`; a run that needed something
else needed a different decision, not a different setting.

## Resume rules

Re-invoking the skill in a repo with an existing workflow directory resumes rather than restarts.

1. Read `state.json`. If `halt` is set, show Magnus the reason first and ask whether to retry that
   step, skip it, or abandon the run. Do not silently retry — the halt was a decision. The single
   exception is rule 6.
2. Otherwise find the first step that is not `done` and start there.
3. **Trust files, not the status field.** A step marked `done` with no file is not done. A file
   that exists beats a status saying pending. The artifacts are the truth.
4. Before resuming at `implement` or later, verify the branch in `state.json` exists and is checked
   out. If Magnus has moved on, stop and ask rather than committing to the wrong branch.
5. A halt whose reason was a **transport failure** — an agent killed by an API error, a stall, or a
   watchdog, having produced nothing — may be retried without asking, up to two attempts. Record
   each attempt in `halt`. Every other halt goes back to Magnus, because every other halt is
   something an agent decided rather than something that happened to it.
6. `commit` has no artifact file. It is done when the branch's HEAD is a commit containing the
   work — check git, not the status field, and never commit twice.
7. `pr` is done when `state.json` holds a URL **and** that PR is open or merged. A `fullRun.merged`
   means the run is finished: report it and do nothing more. Before creating one, check
   for an existing PR on the branch (`gh pr view <branch>`) — a resumed run that opens a second
   pull request for the same branch is a mess someone has to close by hand.
8. **The final run is never resumed into.** It starts only when Magnus says the change has settled
   or asks for a merge, so it has no step, and re-invoking the skill does not start it — or merge
   anything. Report a stale or failed `fullRun`. Do not act on it.

## Multiple runs

One directory per slug; several may coexist. If more than one has incomplete steps and is not
merged, list them and ask which to resume rather than guessing. Finished runs are worth keeping — `plan.md` next to a
merged PR is the best record of why the code looks the way it does.
