---
name: feature
description: Run the full feature workflow — clarify the requirement, plan it with Opus, get approval, implement with Sonnet, review it independently, apply fixes, and ship a pull request. Use whenever Magnus wants to build, add, change, fix, or refactor something in a codebase and the work is bigger than a trivial one-file edit — "I want to implement X", "add X to the app", "fix the bug where X", "refactor X". Also invoked directly as /dev-workflow:feature.
argument-hint: [what you want to build or fix]
---

# Feature workflow

One approval gate, at the plan. Everything after it runs unattended and is recoverable through the
pull request.

```
clarify → PLAN → [approve] → branch + implement → draft PR → review → fix → ready
```

**Do not use this for:** a one-line change, a question about the code, exploration, or anything
where the user is still thinking out loud rather than asking for work. Say what you are about to
do and let them redirect before you spend a planning pass on it. If a request is ambiguous in size,
ask; do not spin up the machinery on a typo fix.

## State

Everything lives in `.claude/workflow/<slug>/` in the target repo. `<slug>` is kebab-case, derived
from the objective (`order-history-pagination`).

| File | Written by | Contains |
|---|---|---|
| `state.json` | orchestrator | step statuses, branch, base, PR number, stack |
| `brief.md` | orchestrator | the clarified requirement |
| `plan.md` | workflow-planner | the approved plan |
| `review.md` | workflow-reviewer | blocking and non-blocking findings |
| `fixes.md` | orchestrator | what was fixed, what was deferred |

**A step counts as done only if its file exists.** That rule is what makes this resumable and what
stops a long chain from silently skipping a step. Never mark a step complete from memory.

On first run in a repo, add the workflow directory to local git excludes so it never lands in a
commit: append `.claude/workflow/` to `.git/info/exclude`.

Read `references/workflow-state.md` for the `state.json` shape and the resume rules.

## Step 0 — Clarify

Talk to the user. This is the only step that cannot be automated and the one that determines
everything downstream.

Ask about anything you cannot answer from the request and the repo: scope boundaries, expected
behaviour at the edges, what is explicitly out of scope, whether an existing pattern should be
followed or replaced. Ask in one batch, not one at a time. Two or three questions that matter beat
a checklist.

Do not ask what you can read. If the repo answers it, read the repo.

If the input is a **design handoff** — a `design/<screen>/` folder, a prototype, a mockup — load
`dev-workflow:design-handoff` now. It changes what you have to ask about: handoffs regularly assert
behaviour the app does not have, and smuggle product decisions in as visual ones. Those are step 0
questions, not something to discover mid-implementation.

Write `brief.md`: the objective, the decisions made in this conversation, and an explicit
out-of-scope list. Confirm nothing — go straight on to planning.

## Step 1 — Plan

Detect the stack first (`references/stack-detection.md`), record it in `state.json`.

Spawn **workflow-planner** (Opus). Give it: the path to `brief.md`, the path to write `plan.md`,
the detected stack, and the repo root. Nothing else — it reads what it needs.

## Gate — the one stop

Show the user the plan's Objective, Conventions applied, Files, and Guard rails. Not the whole
file; they can open it.

If Open questions is non-empty, the plan is not approvable — get answers, hand them back to the
planner, regenerate.

Wait for explicit approval. "Looks good" is approval; silence is not. If they ask for changes,
re-run the planner with their feedback rather than editing the plan yourself — you are on the
orchestrator's context, and hand-editing a plan is how the plan and the reasoning behind it drift
apart.

## Step 2 — Branch and implement

1. Confirm the working tree is clean. If it is not, stop and ask — never start on top of
   uncommitted work.
2. Record the base branch, then create `feature/<slug>` (or `fix/<slug>`). **Never work on the
   default branch.**
3. Spawn **workflow-executor** (Sonnet) with the path to `plan.md`.
4. When it returns, run the plan's verification commands yourself. Do not take its word for it.

**Hard stop:** if verification fails, stop here and report. Never open a PR on a broken build.
**Hard stop:** if the executor reports missing or contradictory plan information, that is a plan
defect — take it back to the user, not into a guess.

Commit with the message convention in `dev-workflow:pr-conventions`.

## Step 3 — Draft PR

```
gh pr create --draft --base <base> --title "<title>" --body-file <body>
```

Body from `dev-workflow:pr-conventions`, marked as review pending. Record the PR number in
`state.json`.

**Hard stop:** if `gh` is missing or unauthenticated, stop here. The branch and commits are safe;
report what remains and let the user open the PR.

## Step 4 — Review

Spawn **workflow-reviewer** with the base ref and the paths to `plan.md` and `review.md`. It gets
no other context about how the change was made — that independence is the entire value of this
step, so do not summarize the implementation into its prompt.

Post the findings to the PR as a comment: `gh pr comment <n> --body-file review.md`.

If the reviewer returned `ESCALATE`, stop. Report to the user and leave the PR in draft. An
architectural problem is not a fix task.

## Step 5 — Fix

**One round only.**

Spawn **workflow-executor** in fix mode with `review.md` and an explicit list of the blocking
findings to address. Non-blocking findings are not assigned — they get deferred.

Re-run verification. Commit the fixes as their own commit so the PR history shows what the review
changed. Write `fixes.md`: fixed, deferred, and anything that could not be fixed without a
decision.

If a second round looks necessary, stop and tell the user. Review–fix ping-pong is a signal that
the plan was wrong, not that another pass is needed.

## Step 6 — Ready

1. Update the PR body: what was built, what the review found, what was fixed, what was deferred
   (with the non-blocking findings listed so they are not lost).
2. `gh pr ready <n>`.
3. Report to the user: PR link, one line on what shipped, and the deferred list.

## Failure handling

Never work around a stop. If something fails, the workflow halts, the state file records where,
and the user decides. A half-finished branch with an honest report is a good outcome; a PR that
papers over a failure is not.

To resume after any stop: re-invoke this skill and it picks up from the first step whose file is
missing.
