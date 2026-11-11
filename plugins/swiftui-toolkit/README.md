# swiftui-toolkit

SwiftUI skills that are procedure, not restated guidance.

## Use it

**HIG.** Add this to the project's `CLAUDE.md`:

```
## UI
UI work follows `swiftui-toolkit:hig`.
```

Then run `dev-workflow:ship` or `feature` as normal. Clarify raises HIG conflicts, the plan cites
the pages it relied on, and the review blocks unapproved deviations.

**Release checkup.** `/swiftui-toolkit:release-checkup`, or with `since v1.2.0` or a path to narrow
it. Six auditors run in parallel and produce one report of work packages, each with a ready ship
brief. It stops for your approval. After that, each approved package runs as a separate
`dev-workflow:ship` session that opens its own pull request. Needs `dev-workflow` installed.

## What it deliberately does not do

**It stores no HIG content.** It fetches the live pages every time. The only data kept here is the
map from a component to the page that covers it.

**It decides no minimum OS, architecture or structure.** Those belong in the project's `CLAUDE.md`.

**The checkup never edits the app and never merges.**

An earlier SwiftUI toolkit was deleted for restating Apple's guidance. This one only knows where the
guidance is and when to apply it.

## What's in here

| Piece | Role |
|---|---|
| `skills/hig` | Fetching the live HIG and SwiftUI docs as JSON, a component-to-page map, what to check at clarify, plan and review |
| `skills/hig/scripts/doc-text.py` | Prints the readable text and child topics of a documentation JSON page |
| `skills/release-checkup` | Orchestrator — scope, audit, merge, report, approval, launch fix sessions |
| `agents/release-auditor` | Fable auditor, one area per spawn, read-only except its findings file |

## Adding to it

The test: *if this doesn't load, does something silently go wrong?* If yes, it is a decision, it
belongs in a project's `CLAUDE.md`, and it must not go here. A skill here must also not restate what
Apple documents. It either fetches it or encodes a procedure.
