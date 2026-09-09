---
name: feature
description: Run the full feature workflow — clarify the requirement, plan it with Opus, get approval, implement with Sonnet, review it from a fresh context, apply fixes, commit and push, then hand the diff to Magnus. Use whenever Magnus wants to build, add, change, fix, or refactor something in a codebase and the work is bigger than a trivial one-file edit — "I want to implement X", "add X to the app", "fix the bug where X", "refactor X". Also invoked directly as /dev-workflow:feature. Does not open a pull request — Magnus does that himself once he has read the diff.
argument-hint: [what you want to build or fix]
---

# Feature workflow

Two stops: the plan, and the finished diff. Between them the work runs unattended. After the
second one, Magnus decides what the team sees.

```
clarify → PLAN → [approve] → branch + implement → review → fix → commit + push → [read the diff] → revise
```

**Do not use this for:** a one-line change, a question about the code, exploration, or anything
where the user is still thinking out loud rather than asking for work. Say what you are about to
do and let them redirect before you spend a planning pass on it. If a request is ambiguous in size,
ask; do not spin up the machinery on a typo fix.

## The workflow does not open a pull request

It stops with a pushed branch and a report in chat. Magnus reads the diff, raises what he wants
changed, and opens the PR himself when it is worth other people's time.

That boundary is the point of the redesign, and it has a second half: **plan, implement, review and
fix are steps in building the thing, not events worth documenting.** They produce local files under
`.claude/workflow/` and nothing else. Do not post them, do not narrate them into a PR body, do not
write commit messages that describe the process rather than the change. When the PR does go up it
should read as though a person wrote the code and knew what they were doing — because one did, and
the machinery that helped is not news to the reviewer.

Concretely, in this workflow: **nothing is ever written to GitHub except the branch and its
commits.** No PR, no comments, no inline findings, no summary threads.

Responding to review feedback once the PR is up is real work, but it is not this skill. It is a
conversation with the team, and it starts after this workflow has ended.

## State

Everything lives in `.claude/workflow/<slug>/` in the target repo. `<slug>` is kebab-case, derived
from the objective (`order-history-pagination`).

| File | Written by | Contains |
|---|---|---|
| `state.json` | orchestrator | step statuses, branch, base, stack |
| `brief.md` | orchestrator | the clarified requirement |
| `plan.md` | workflow-planner | the approved plan |
| `review.md` | workflow-reviewer | blocking and non-blocking findings |
| `fixes.md` | orchestrator | what was fixed, what was deferred |

**A step counts as done only if its file exists.** That rule is what makes this resumable and what
stops a long chain from silently skipping a step. Never mark a step complete from memory.

On first run in a repo, add the workflow directory to local git excludes so it never lands in a
commit: append `.claude/workflow/` to `.git/info/exclude`. Do this **before** anything is staged —
the run stages with `git add -A`, and an unexcluded workflow directory would ride along into the
commit and then into the PR.

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

## Gate — the approval

Show the user the plan's Objective, Conventions applied, Files, and Guard rails. Not the whole
file; they can open it.

Alongside it, state the **implementer model** in one line — Sonnet by default. Say Haiku instead if
the plan came back mechanical: a long list of near-identical edits, a rename, a scaffold,
generated-code wiring. Judge this from the plan you now have, not from the request. Magnus can
override either way.

If Open questions is non-empty, the plan is not approvable — get answers, hand them back to the
planner, regenerate.

Wait for explicit approval. "Looks good" is approval; silence is not. If they ask for changes,
re-run the planner with their feedback rather than editing the plan yourself — you are on the
orchestrator's context, and hand-editing a plan is how the plan and the reasoning behind it drift
apart.

## Step 2 — Branch and implement

1. `git fetch`. Base-branch decisions go stale exactly this way — a local ref that predates a merge
   turns into a question for the user that a fetch would have answered.
2. Confirm the working tree is clean. If it is not, stop and ask — never start on top of
   uncommitted work.
3. Record the base branch, then create `feature/<slug>` (or `fix/<slug>`). **Never work on the
   default branch.**
4. Spawn **workflow-executor** with the path to `plan.md`, on the model confirmed at the gate.
5. When it returns, run the plan's verification commands yourself. Do not take its word for it.
6. `git add -A`. **Stage, do not commit.** The commit comes after the review, so that a run ending
   clean produces one commit rather than a trail of them — and staging is what gives the reviewer a
   diff to read, since `HEAD` is still the base commit at that point.

**Build from scratch before making any claim about warnings.** An incremental build reports zero
warnings for a file it did not recompile, which is how "builds clean" ends up in a report untrue.
Incremental is fine for "tests pass". It is not evidence about warnings. Record which kind you ran.

**Hard stop:** if verification fails, stop here and report. **Hard stop:** if the executor reports
missing or contradictory plan information, that is a plan defect — take it back to the user, not
into a guess.

## Step 3 — Review

Spawn **workflow-reviewer** with the base ref and the paths to `plan.md` and `review.md`. It reads
the staged diff — `git diff --cached <base>` — because nothing is committed yet. It gets no other
context about how the change was made; that independence is the entire value of this step, so do
not summarize the implementation into its prompt.

It writes its findings to `review.md` and returns the blocking count. That file is for step 4 and
for your report at the handoff. It goes nowhere else.

If the reviewer returned `ESCALATE`, stop. Report to the user; the work stays staged and
uncommitted on the branch. An architectural problem is not a fix task.

This is the review the workflow owes you, not the only review that exists. If the change deserves a
harder look, Magnus asks for one — `/code-review high`, `/code-review ultra`, or a lens of his
choosing — at the handoff, where he can see what he is deciding about.

## Step 4 — Fix

One round. Spawn **workflow-executor** in fix mode with `review.md` and an explicit list of the
blocking findings to address. Non-blocking findings are not assigned — they get deferred and
reported.

Re-run verification afterwards yourself, then `git add -A` again so the fixes join the staged work.

If the review came back with nothing blocking, there is no executor round — but still write
`fixes.md`, recording the deferred non-blocking findings. The step is done when the file exists,
and a clean review with no file looks identical to a skipped step.

**Stop and escalate if the reviewer's findings turn out to need a design decision** rather than a
fix, or if verification fails after the fix round. Both mean the plan was wrong, and another
unattended pass will not make it right.

Write `fixes.md`: fixed, deferred, and anything that could not be fixed without a decision.

## Step 5 — Commit and push

One commit for the whole run — implementation and review fixes together, already staged. The
review was a step in building this, not a change to it, so it does not get its own entry in the
history.

Message from `dev-workflow:pr-conventions`: describe the change, not the process. Nothing about
plans, reviews, agents, or steps.

Then `git push -u origin <branch>`.

**Hard stop:** if the push is rejected or the remote is unreachable, report it. The commit is safe
locally and the user can push it themselves.

## Step 6 — Handoff

Stop and report. Keep it to what Magnus needs in order to read the diff:

- The branch, and `git diff <base>...HEAD` so he can open it in one paste.
- One or two lines on what was built.
- Verification: what ran, which build kind backs any warnings claim.
- Deferred non-blocking findings, one line each — this is the only place they surface, so do not
  drop them.
- Anything a reader would not predict from the diff: a codegen pass, a bulk rename, a dependency
  that came along.

Then wait. He reads it, asks questions, and says what he wants changed.

**Revisions.** Implement what he asks for directly — you have the context, and a round of small
agreed changes does not need the planner. Re-run verification, commit each agreed round as its own
commit, and push. Those commits are his changes, not review fixes, and their messages say what
changed.

If a request is large enough to be a different feature, say so and start a new run rather than
growing this one.

The workflow ends here. Magnus opens the pull request when he decides the branch is worth the
team's time.

## Failure handling

Three buckets, and the distinction matters: a single rule of "never work around a stop" reads as
*halt*, which is right for an agent that reports a problem and wrong for one whose transport
dropped.

**Transport failure** — an agent killed by an API error, a stall, or a watchdog, having produced
nothing. Not a finding. **Resume it by message**, which preserves its transcript, rather than
spawning a fresh one and paying for the context again. Two attempts, then halt and report.

**Judgment needed** — the reviewer returns `ESCALATE`, the executor hits missing or contradictory
plan information, verification fails, the tree is dirty, the push is rejected. **Halt.** The state
file records where, and the user decides.

**Everything else** — keep going to the handoff. That is what the approval bought.

On any halt, if a notification tool is available, use it. The point of a single gate is that Magnus
walks away after approving; a run that halts silently wastes the time it was meant to save.

A half-finished branch with an honest report is a good outcome; a clean-looking one that papers
over a failure is not. To resume after any stop: re-invoke this skill and it picks up from the
first step whose file is missing.
