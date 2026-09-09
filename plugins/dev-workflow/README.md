# dev-workflow

The feature loop: **clarify → plan (Opus) → approve → implement (Sonnet) → review → fix → commit and
push → hand over the diff.** Two stops — the plan, and the finished branch.

It does not open a pull request. It ends with a pushed branch and a short report; Magnus reads the
diff, says what he wants changed, and opens the PR himself when it is worth the team's time.

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
| `skills/feature` | The orchestrator — state machine, gate, handoff, resume |
| `skills/plan-format` | What makes a plan executable by an agent that won't push back |
| `skills/pr-conventions` | Branch, commit, and PR body structure, and the voice for anything posted to GitHub |
| `skills/testing-doctrine` | What to test and why — stack-agnostic; the project supplies the patterns |
| `skills/design-handoff` | Turning a design tool's output into shipped UI, and what to verify first |
| `agents/workflow-planner` | Opus. Reads the repo, writes the plan, writes nothing else |
| `agents/workflow-executor` | Sonnet. Executes the plan faithfully, or applies assigned fixes |
| `agents/workflow-reviewer` | Reviews the diff with no knowledge of how it was written |

## Design notes

**Plan, implement, review and fix are steps in building the thing, not events to document.** They
write local files under `.claude/workflow/` and nothing else. Nothing about the process reaches
GitHub — not in a commit message, not in a PR body, not as a comment. A reviewer opening the PR
should see a change someone made on purpose, which is what it is; how it was made is not news to
them, and narrating it is how a PR ends up longer than the diff.

The corollary is that a run produces **one commit**. Implementation and review fixes land together,
because the review was part of writing the code rather than a change to it. Only what Magnus asks
for after the handoff gets commits of its own.

**The workflow stops before the PR.** A PR is a request for other people's attention, and only
Magnus knows when the branch has earned it. So the run ends at a pushed branch with a report: what
was built, what was verified, what was deferred, and the command to open the diff. What happens
next — questions, revisions, and eventually a PR — is a conversation, not a step in a state
machine.

**One review, run blind.** An agent cannot review code it just wrote; it defends the reasoning it
already holds. The reviewer sees the diff and the plan and nothing about how the change was
produced. It runs `code-review` at its default effort and adds the two checks that need the plan —
conformance to the plan, and to the conventions the plan recorded. A change that deserves a harder
look gets one because Magnus asks for it at the handoff, where he can see what he is deciding
about, rather than because a flag was set before anyone had seen the code.

**File-based handoff.** Every step writes an artifact to `.claude/workflow/<slug>/`. Subagents
return summaries, not context — so the plan the implementer reads is the plan on disk, not a
paraphrase. It also makes the run resumable: a step counts as done only if its file exists.

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

**Nothing here requires a particular layout, and there is no setup step.** A repo with
`CLAUDE.md`, `android/CLAUDE.md` and `ios/CLAUDE.md` just works — the nearest file wins over the
root, and the plan says which won. Writing those files is the project owner's job; this workflow
reads them and will never ask you to reorganize a project to suit it.

If a project states nothing, the planner says so rather than inventing some — a convention it made
up and recorded as though the project chose it is worse than a gap.

Precedence, highest first: an instruction in the session → the nearest applicable `CLAUDE.md` →
the root `CLAUDE.md` → what those point at → existing patterns in the repo.
