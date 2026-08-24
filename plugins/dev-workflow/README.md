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

## What's in here

| Piece | Role |
|---|---|
| `skills/feature` | The orchestrator — state machine, gate, PR flow, resume |
| `skills/plan-format` | What makes a plan executable by an agent that won't push back |
| `skills/pr-conventions` | Branch, commit, and PR body structure |
| `skills/testing-doctrine` | What to test and why — stack-agnostic; the stacks supply the patterns |
| `skills/design-handoff` | Turning a design tool's output into shipped UI, and what to verify first |
| `agents/workflow-planner` | Opus. Reads the repo, writes the plan, writes nothing else |
| `agents/workflow-executor` | Sonnet. Executes the plan faithfully, or applies assigned fixes |
| `agents/workflow-reviewer` | Reviews the diff with no knowledge of how it was written |

## Design notes

**File-based handoff.** Every step writes an artifact to `.claude/workflow/<slug>/`. Subagents
return summaries, not context — so the plan the implementer reads is the plan on disk, not a
paraphrase. It also makes the run resumable: a step counts as done only if its file exists.

**The reviewer is context-blind.** An agent cannot review code it just wrote; it defends the
reasoning it already holds. The reviewer sees the diff and the plan, and nothing about how the
change was produced.

**One fix round.** Reviewers always find something. Blocking findings are fixed, nits are deferred
to the PR body, and a second round means the plan was wrong — which is a conversation, not another
pass.

**Doctrine is shared, patterns are local.** What to test and why does not change between Flutter,
SwiftUI, and whatever comes next, so it lives here in `testing-doctrine` and each toolkit's testing
skill supplies only the stack's patterns. The same split applies to design handoffs and PR
structure. A new stack needs a conventions skill and a verification entry; it inherits the rest.

**Conventions are fetched, not remembered.** The planner invokes the stack's conventions skill and
records every binding choice in the plan's *Conventions applied* table. Skill auto-triggering is
probabilistic; an explicit invocation is not.

Precedence for conventions, highest first: an instruction in the session → the project's
`CLAUDE.md` or `.claude/conventions/<stack>.md` → existing patterns in the repo → the toolkit
conventions skill.
