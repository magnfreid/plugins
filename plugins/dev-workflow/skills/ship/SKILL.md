---
name: ship
description: Run the feature workflow end to end — clarify the requirement, plan it with Opus, implement with Sonnet, review it from a fresh context, apply fixes, commit, push, and open the pull request. One interaction, at the start. Use whenever Magnus wants to build, add, change, fix, or refactor something in a repo whose CLAUDE.md names this workflow — "I want to implement X", "add X to the app", "fix the bug where X" — or when invoked directly as /dev-workflow:ship. Opens the PR; never merges it.
argument-hint: [what you want to build or fix]
---

# Ship workflow

One stop, at the beginning. Everything after the clarifying questions runs unattended and ends at
a pull request Magnus can read and merge.

```
clarify → plan → branch + implement → review → fix → commit + push → PR
```

This is `dev-workflow:feature` with the two gates removed and the PR added. Everything else —
the planner, the executor, the reviewer, the plan format, the conventions, the state files — is
identical, and where this file is silent, `feature`'s rules apply.

**Use `feature` instead when Magnus wants to read the diff before anyone else sees it.** This
skill is for repos that have opted into it: he reviews by running the app and reporting bugs, not
by reading the branch. Do not switch a project to this flow on your own initiative — its
`CLAUDE.md` says which one it uses.

**Do not use either for:** a one-line change, a question about the code, exploration, or anything
where the user is still thinking out loud. Say what you are about to do and let them redirect. If
a request is ambiguous in size, ask.

## What is different, and why

**No approval gate.** The clarify step carries the whole weight of getting it right, so spend the
questions there. Everything downstream is recoverable through the PR — Magnus can reject a branch,
and a rejected branch costs one run.

**It opens the PR.** Not a draft. A PR nobody has read is still the thing being asked for: Magnus
merges it, or he runs the app, finds a bug, and reports it. **Never merge it yourself**, and never
enable auto-merge.

**The review is harder, because no human reads the diff.** Tell `workflow-reviewer` to invoke the
`code-review` skill at **`high`** effort rather than its default. That is one line in its prompt.
Do not add a second standalone review pass — the reviewer already runs `code-review` inside itself,
and a second run over the same diff mostly re-finds what the first one found.

**Tests are not optional.** `dev-workflow:testing-doctrine` still decides *what* a test should
assert, but the bar for *whether* is raised: **every behavioural change ships with a test that
would fail without it.** Say this in the planner's prompt so it lands in the plan, and treat a
missing test as a blocking finding at review. Pure refactors with existing coverage, formatting,
and documentation are exempt — nothing about their behaviour changed.

**The PR body carries a manual test plan.** Numbered steps Magnus can follow in the running app,
because that is how he reviews. See `dev-workflow:pr-conventions`.

## State

`.claude/workflow/<slug>/`, exactly as `feature` uses it — `state.json`, `brief.md`, `plan.md`,
`review.md`, `fixes.md`. **A step counts as done only if its file exists.** Never mark a step
complete from memory.

Read `references/workflow-state.md` for this flow's `state.json` shape and resume rules. They
differ from `feature`'s in two places: there is no `approved` step, and there is a `pr` step.

On first run in a repo, append `.claude/workflow/` to `.git/info/exclude` **before** anything is
staged. The run stages with `git add -A`, and an unexcluded workflow directory rides along into the
commit and then into the PR.

## Step 0 — Clarify

The only conversation in the run. It is doing the job two gates used to do, so do it properly.

Ask about anything you cannot answer from the request and the repo: scope boundaries, behaviour at
the edges, what is explicitly out of scope, whether an existing pattern is being followed or
replaced. Ask in one batch. Two or three questions that matter beat a checklist.

Do not ask what you can read. If the repo answers it, read the repo.

Ask the question you would otherwise have raised at the plan gate. There is no gate — a decision
you defer here is one that gets made without him.

If the input is a **design handoff** — a `design/<screen>/` folder, a prototype, a mockup — load
`dev-workflow:design-handoff` now. Handoffs assert behaviour the app does not have and smuggle
product decisions in as visual ones. Those are step 0 questions.

Write `brief.md`: the objective, the decisions taken in this conversation, and an explicit
out-of-scope list. Then go, without confirming.

## Step 1 — Plan

Detect the stack first — `../feature/references/stack-detection.md`, shared with `feature` so a new
stack is added in one place — and record it in `state.json`.

Spawn **workflow-planner** (Opus) with: the path to `brief.md`, the path to write `plan.md`, the
detected stack, the repo root, and the raised testing bar above. Nothing else — it reads what it
needs.

**Open questions are the one thing that can pull Magnus back in.** If the plan comes back with a
non-empty Open questions section, stop and ask him. Do not answer them yourself: the planner
raising a question means it could not choose from the repo, and a guess recorded as a decision is
exactly the failure this workflow is supposed to prevent. Feed the answers back and regenerate.
A clarify step that did its job makes this rare.

**Choose the implementer yourself.** Sonnet by default; Haiku when the plan came back mechanical —
a long list of near-identical edits, a rename, a scaffold, generated-code wiring. Judge from the
plan, not the request. Record it in `state.json` as `implementer`.

## Step 2 — Branch and implement

1. `git fetch`. A base-branch decision from a stale local ref is how a run ends up branched off a
   commit that was merged away.
2. Confirm the working tree is clean. If it is not, stop and ask — never start on top of
   uncommitted work.
3. Record the base branch, then create `feature/<slug>` (or `fix/<slug>`). **Never work on the
   default branch.**
4. Spawn **workflow-executor** with the path to `plan.md`, on the chosen model.
5. When it returns, run the plan's verification commands yourself. Do not take its word for it.
6. `git add -A`. **Stage, do not commit.** The commit comes after the review, so a clean run
   produces one commit — and staging is what gives the reviewer a diff, since `HEAD` is still the
   base commit at that point.

**Build from scratch before making any claim about warnings.** An incremental build reports zero
warnings for a file it did not recompile. Incremental is fine for "tests pass". Record which you
ran; it goes in the PR body.

**Hard stop** if verification fails. **Hard stop** if the executor reports missing or contradictory
plan information — that is a plan defect, and it goes back to Magnus rather than into a guess.

## Step 3 — Review

Spawn **workflow-reviewer** with the base ref, the paths to `plan.md` and `review.md`, and the
instruction to run `code-review` at **`high`**. It reads the staged diff — `git diff --cached
<base>` — and gets no other context about how the change was made. That independence is the whole
value of the step: do not summarize the implementation into its prompt.

Add one item to its brief: **a behavioural change with no test is a blocking finding.**

If it returns `ESCALATE`, stop. Report to Magnus; the work stays staged and uncommitted on the
branch. An architectural problem is not a fix task, and it is not something to open a PR about.

## Step 4 — Fix

One round. Spawn **workflow-executor** in fix mode with `review.md` and an explicit list of the
blocking findings. Non-blocking findings are not assigned — they are deferred and reported.

Re-run verification yourself, then `git add -A` again.

If the review came back with nothing blocking there is no executor round, but **still write
`fixes.md`** recording the deferred findings. The step is done when the file exists, and a clean
review with no file looks identical to a skipped step.

**Stop and escalate** if a finding needs a design decision rather than a fix, or if verification
fails after the fix round. Both mean the plan was wrong, and another unattended pass will not fix
that.

## Step 5 — Commit and push

One commit for the run — implementation and review fixes together, already staged. The review was
a step in building this, not a change to it.

Message per `dev-workflow:pr-conventions`: describe the change, not the process. Nothing about
plans, reviews, agents, or steps.

Then `git push -u origin <branch>`.

**Hard stop** if the push is rejected or the remote is unreachable. The commit is safe locally.

## Step 6 — Open the pull request

Body per `dev-workflow:pr-conventions`, including its **Test plan** section. Two things matter
more here than anywhere else, because this body is the only description of the change anyone will
read:

- **Short.** Magnus reads every one of these. A body longer than it needs to be is one he skims,
  and skimming is where a flagged risk gets missed.
- **Written for a junior developer who was not in the conversation** — plain words, what changed
  and what to look at, no pattern names used as shorthand.

Then record the URL in `state.json` and report it in chat with:

- What was built, in a line or two.
- Verification: what ran, and which build kind backs any warnings claim.
- Deferred non-blocking findings, one line each. This is the only place they surface.
- Anything a reader would not predict from the diff — a codegen pass, a bulk rename, a dependency
  that came along.

**Never merge, and never enable auto-merge.** Merging is the decision this whole workflow exists
to hand to Magnus.

**Revisions** — bugs he finds in the running app, changes he asks for — are implemented directly
on the same branch and pushed as their own commits, named for what changed. You have the context;
a round of small agreed changes does not need the planner. Re-run verification each time. If a
request is large enough to be a different feature, say so and start a new run.

## Failure handling

Three buckets. The distinction matters: one rule of "never work around a stop" reads as *halt*,
which is right for an agent that reported a problem and wrong for one whose transport dropped.

**Transport failure** — an agent killed by an API error, a stall, or a watchdog, having produced
nothing. Not a finding. **Resume it by message**, preserving its transcript, rather than spawning
a fresh one and paying for the context again. Two attempts, then halt.

**Judgment needed** — the reviewer returns `ESCALATE`, the executor hits missing or contradictory
plan information, the plan has open questions, verification fails, the tree is dirty, the push is
rejected. **Halt.** `state.json` records where, and Magnus decides.

**Everything else** — keep going to the PR.

On any halt, **notify** if a notification tool is available. This flow exists so Magnus can walk
away after the clarifying questions; a run that halts silently wastes exactly the time it was
meant to save.

**Never open a PR to cover a halt.** A pull request is a statement that the branch is ready to
merge. A half-finished branch with an honest report in chat is a good outcome; a PR that looks
finished and is not costs him a merge he has to undo.

To resume after any stop, re-invoke this skill: it picks up from the first step whose file is
missing.
