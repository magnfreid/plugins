---
name: feature
description: Run the full feature workflow — clarify the requirement, plan it with Opus, get approval, implement with Sonnet, review it independently, apply fixes, and ship a pull request. Use whenever Magnus wants to build, add, change, fix, or refactor something in a codebase and the work is bigger than a trivial one-file edit — "I want to implement X", "add X to the app", "fix the bug where X", "refactor X". Also invoked directly as /dev-workflow:feature, optionally with --deep-review (or --deep) to replace the standard review with a deeper one in the same run.
argument-hint: [what you want to build or fix] [--deep-review]
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

## Levels

`--deep-review` (`--deep` is accepted as a shorthand) changes step 4 and step 5. Nothing else. It
**replaces** the standard review rather than adding a pass after it — there is one review phase per
run, and the level decides who is in it.

Everything not in this table — plan conformance, convention conformance, independent verification,
the from-scratch build — is unconditional and does not vary with the level.

| | default | `--deep-review` |
|---|---|---|
| `code-review` effort | its own default | `high` |
| Review lenses | `workflow-reviewer` | + `workflow-failure-reviewer`, in parallel, + any review agents the project's `CLAUDE.md` names |
| Fix rounds | one, total | one per reviewer that filed blocking findings, capped at 3 fix commits |

The default is deliberately *exactly* what a fresh-context code review gives you, plus the two
checks that need the plan. It is the right level for most work. Reach for `--deep-review` when the
change crosses a trust boundary, touches money or auth, is implemented twice (two platforms, two
call sites), or is large enough that you would not read the whole diff yourself.

Record the level in `state.json` at step 0 so a resumed run does not silently change level
mid-flight.

## State

Everything lives in `.claude/workflow/<slug>/` in the target repo. `<slug>` is kebab-case, derived
from the objective (`order-history-pagination`).

| File | Written by | Contains |
|---|---|---|
| `state.json` | orchestrator | step statuses, level, branch, base, PR number, stack |
| `brief.md` | orchestrator | the clarified requirement |
| `plan.md` | workflow-planner | the approved plan |
| `review.md` | workflow-reviewer | blocking and non-blocking findings |
| `review-<lens>.md` | each extra reviewer | one file per additional lens, `--deep-review` only |
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

Do not ask what you can read. If the repo answers it, read the repo. **The level is not a question
either** — take it from the invocation, and if the change looks like one of the `--deep-review` cases
above while the user did not ask for it, say so once at the gate rather than interrupting here.
Flag it in the report at the end too if it was declined and the review then found blocking work.

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

Alongside it, state in one line each — these are the settings the rest of the run uses, and this
is the last moment to change them without stopping the machinery again:

- **Review level**, and if the plan turned out to hit a `--deep-review` case they did not ask for, that.
- **Implementer model** — Sonnet by default. Say Haiku instead if the plan came back mechanical:
  a long list of near-identical edits, a rename, a scaffold, generated-code wiring. Judge this from
  the plan you now have, not from the request. Magnus can override either way.

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

**Build from scratch before making any claim about warnings.** An incremental build reports zero
warnings for a file it did not recompile, which is how "builds clean" ends up in a PR body untrue.
Incremental is fine for "tests pass". It is not evidence about warnings. Record which kind you ran.

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

The draft PR from step 3 is what makes this step readable: findings land on the PR, fixes land as
commits under them, and the whole exchange is still there when you open it. That is why the PR is
opened before the review rather than after it.

Spawn **workflow-reviewer** with the base ref, the PR number, the paths to `plan.md` and
`review.md`, and the `code-review` effort for this level. It gets no other context about how the change was made — that
independence is the entire value of this step, so do not summarize the implementation into its
prompt.

**At `--deep-review`, spawn these in parallel with it**, each with the same inputs and its own findings
file:

- **workflow-failure-reviewer** → `review-failure.md`. A second lens scoped to failure modes rather
  than correctness in general. It exists because the two find near-disjoint sets: a correctness
  sweep reads a swallowed error or a stale projection as reasonable code.
- **Any review agents the project's own `CLAUDE.md` names** for this kind of change. If it names
  none, nothing extra runs. This is what makes a project's review table load-bearing instead of
  decorative, and it keeps project-specific policy out of this skill.

**Posting the findings.** Two forms, and they are not redundant:

- **Inline, on the line.** `workflow-reviewer` passes `--comment` to the `code-review` skill, which
  anchors each of its findings to the line it is about. This is the form worth reading — a finding
  next to its code needs no explaining.
- **A summary comment per findings file**, `gh pr comment <n> --body-file <file>`. This one is
  authoritative: it is what step 5 reads, it carries the plan- and convention-conformance findings
  that have no single line to sit on, and it survives when inline comments are marked outdated by
  the fixes that answer them.

Lenses other than `workflow-reviewer` post the summary form only — their findings cite `file:line`
in the text, which is navigable, and hand-assembling review payloads for them would add a fragile
step to the one part of this workflow that must not fail quietly.

Whatever is still open at the end goes in the **PR body** as well. A squash merge takes every
comment thread with it; the body is the only part that survives into the history.

If any reviewer returned `ESCALATE`, stop. Report to the user and leave the PR in draft. An
architectural problem is not a fix task.

**What may cross between reviewers.** On a retry, a resume, or a reviewer spawned after another has
already reported, you may pass the findings already filed, so it stops re-deriving them and spends
its budget on new ground. You may **never** pass implementation rationale. Findings are review
output; rationale is the implementer's reasoning, and passing that is what would cost independence.

## Step 5 — Fix

| Level | Rounds |
|---|---|
| default | One round, total. |
| `--deep-review` | One round per reviewer that filed blocking findings. Hard cap of 3 fix commits. |

Spawn **workflow-executor** in fix mode with the findings file and an explicit list of the blocking
findings to address. Non-blocking findings are not assigned — they get deferred. Re-run
verification. Commit each round as its own commit so the PR history shows what each review changed;
never amend or force-push a branch under review.

**Stop and escalate when the *same* reviewer comes back with new blocking findings** after its
round. That is the signal that the plan was wrong rather than that another pass is needed. A
*different* reviewer finding something the first did not is the system working, not ping-pong.

At the cap, stop even with findings outstanding: write them into the PR body and report. An
unattended run may end incomplete; it may never end incomplete and silent.

Write `fixes.md`: fixed, deferred, and anything that could not be fixed without a decision.

## Step 6 — Ready

1. Update the PR body: what was built, which build kind backs the verification claims, what the
   review found, what was fixed, what was deferred (with the non-blocking findings listed so they
   are not lost).
2. `gh pr ready <n>`.
3. Report to the user: PR link, one line on what shipped, the deferred list, and — if the diff is
   large enough that a deeper pass would pay (roughly 1000+ lines or 25+ files) — that
   `/code-review ultra` is worth running by hand. That one is user-triggered and billed, so this
   workflow cannot launch it; saying so is the most it can do.

## Failure handling

Three buckets, and the distinction matters: the old single rule of "never work around a stop" reads
as *halt*, which is right for an agent that reports a problem and wrong for one whose transport
dropped.

**Transport failure** — an agent killed by an API error, a stall, or a watchdog, having produced
nothing. Not a finding. **Resume it by message**, which preserves its transcript, rather than
spawning a fresh one and paying for the context again. Two attempts, then halt and report.

**Judgment needed** — a reviewer returns `ESCALATE`, the executor hits missing or contradictory
plan information, verification fails, the tree is dirty, `gh` is unauthenticated, the fix cap is
reached. **Halt.** The state file records where, the PR stays in draft, and the user decides.

**Everything else** — keep going to the PR. That is what the approval bought.

On any halt, if a notification tool is available, use it. The point of a single gate is that Magnus
walks away after approving; a run that halts silently wastes the time it was meant to save.

A half-finished branch with an honest report is a good outcome; a PR that papers over a failure is
not. To resume after any stop: re-invoke this skill and it picks up from the first step whose file
is missing.
