# dev-workflow

The feature loop: **clarify → plan (Opus) → approve → implement (Sonnet) → draft PR → independent
review → fix → ready.** One approval gate, at the plan. Everything after it is recoverable through
the PR.

## Use it

```
I want to add pagination to the order history screen
```

or explicitly:

```
/dev-workflow:feature paginate the order history screen
```

Both enter at step 0 and ask whatever is unclear before any planning happens.

Add `--deep-review` (or `--deep`) to swap the standard review for a deeper one **in the same run** —
not a second pass layered on top of the first:

```
/dev-workflow:feature --deep-review migrate the session store to the new token API
```

## What's in here

| Piece | Role |
|---|---|
| `skills/feature` | The orchestrator — state machine, gate, PR flow, resume |
| `skills/plan-format` | What makes a plan executable by an agent that won't push back |
| `skills/pr-conventions` | Branch, commit, and PR body structure |
| `skills/testing-doctrine` | What to test and why — stack-agnostic; the project supplies the patterns |
| `skills/design-handoff` | Turning a design tool's output into shipped UI, and what to verify first |
| `agents/workflow-planner` | Opus. Reads the repo, writes the plan, writes nothing else |
| `agents/workflow-executor` | Sonnet. Executes the plan faithfully, or applies assigned fixes |
| `agents/workflow-reviewer` | Reviews the diff with no knowledge of how it was written |
| `agents/workflow-failure-reviewer` | `--deep-review` only. Second lens: swallowed errors, boundaries, stale state, divergence |

## Design notes

**The PR is the middle of the run, not the end.** It opens as a draft *before* the review so the
findings have somewhere to attach: comments land on the draft, fix commits land under them, and it
only goes ready once the body reflects the final state. Findings post twice on purpose — inline on
the line they concern, for reading, and as a summary comment, which is what the fix step reads and
what survives fixes marking the inline ones outdated. Anything still open also goes in the PR body,
because a squash merge takes every comment thread with it.

**File-based handoff.** Every step writes an artifact to `.claude/workflow/<slug>/`. Subagents
return summaries, not context — so the plan the implementer reads is the plan on disk, not a
paraphrase. It also makes the run resumable: a step counts as done only if its file exists.

**The reviewer is context-blind.** An agent cannot review code it just wrote; it defends the
reasoning it already holds. The reviewer sees the diff and the plan, and nothing about how the
change was produced.

**Two levels, differing in one step.** The default review is exactly what a fresh-context
`code-review` gives you, plus the two checks that need the plan — conformance to it, and to the
conventions it recorded. `--deep-review` raises the `code-review` effort to `high` and adds a second lens
running in parallel, plus any review agents the *project's* `CLAUDE.md` names. Nothing else about
the workflow changes, and the settings that protect the result — independent verification, a
from-scratch build behind any warnings claim, one approval gate — are unconditional.

**The second lens does not overlap the first.** Two reviewers running the same sweep cost twice and
find the same things. `workflow-failure-reviewer` is scoped to what a correctness pass
systematically under-weights: errors that are caught and dropped, boundary inputs that trap, a
write that never reaches the representation the reader reads, and two implementations of one
contract that disagree about the empty case.

**Fix rounds are per reviewer, not per run.** Reviewers always find something, and one round each
is how a second lens earns its keep. What signals a bad plan is the *same* reviewer coming back
with new blocking findings after its round — that escalates. A different reviewer finding something
the first missed is the system working. Three fix commits is the hard cap either way; past it the
run stops and writes the remainder into the PR body.

**Halts are triaged, not uniform.** An agent that reports a defect halts the run. An agent whose
transport dropped — API error, stall, watchdog — is resumed by message, which keeps its transcript
instead of paying for the context twice. Conflating the two is how a workflow either stops on
nothing or grinds past something real.

**Doctrine is shared, conventions are the project's.** What to test and why does not change
between Flutter, SwiftUI, and whatever comes next, so it lives here in `testing-doctrine`. What
*does* change — which state library, which folder tree, which APIs are banned — lives in the target
repo's own `CLAUDE.md`, because a rule that must hold every time cannot depend on a skill
triggering. A new stack needs a verification entry in `stack-detection.md` and nothing else.

**Conventions are discovered, not required.** The planner reads whatever the project states, in
whatever shape it states it: a `CLAUDE.md` at every level covering the change, the docs those point
at, and — where nothing is written down — the patterns already in the code. It records every
binding choice in the plan's *Conventions applied* table with the source it came from, and the
reviewer checks that table against the diff, which is what makes an unhonoured convention a
blocking finding rather than a matter of taste.

**Nothing here requires a particular layout.** A repo with `CLAUDE.md`, `android/CLAUDE.md` and
`ios/CLAUDE.md` needs no setup step — the nearest file wins over the root, and the plan says which
won. The toolkits' `init-conventions` commands are a shortcut for a project that has *not* written
its rules down yet; they are never a prerequisite, and this workflow will not ask you to reorganize
a project to suit it.

If a project states nothing, the planner says so rather than inventing some — a convention it made
up and recorded as though the project chose it is worse than a gap.

Precedence, highest first: an instruction in the session → the nearest applicable `CLAUDE.md` →
the root `CLAUDE.md` → what those point at → existing patterns in the repo.
