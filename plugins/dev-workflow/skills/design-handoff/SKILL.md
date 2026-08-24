---
name: design-handoff
description: How a visual design arriving from a design tool becomes shipped UI — where handoff material lives in the repo, why the prototype is reference and never ported, and what a planning pass has to verify before any of it is implemented. Load when a design, mockup, prototype, or handoff folder is the input to a change.
---

# Design handoffs

A handoff is source material from a visual design tool, kept in the repo so an implementation plan
can cite exact values instead of re-deriving them from a screenshot.

The handoff directory holds **input**. The executable plan derived from it lives wherever plans live
and links back to the handoff.

## Layout

```
design/
  README.md                 the project's own notes, if any
  <screen-name>/            one directory per handoff, kebab-case
    HANDOFF.md              the spec: layout, tokens, copy, files touched
    <prototype>            the reference prototype (HTML, PDF, image set)
    <runtime>              anything the prototype needs to render — vendored, never edited
```

Name the directory after **the screen**, not the design option or the date: `interview-chat/`, not
`interview-chat-2d/` or `handoff-2026-08-19/`. Option numbers are exploration history and stop
meaning anything once one is chosen — the chosen option is recorded inside `HANDOFF.md`.

A screen redesigned again **overwrites its directory**. Version control holds the previous version;
a second directory with a suffix does not, it just rots.

## Rules

- **The prototype is reference, never a source to port.** It exists to pin down colour, spacing, and
  motion. Recreate it in the app's actual stack, following the patterns already in the codebase. No
  CSS is translated. No second styling approach enters the project because one screen was designed
  elsewhere.
- **Every colour, font, radius, and spacing value the handoff introduces becomes a token** in the
  project's design-token layer — never a literal in a feature widget. If the handoff names a value
  no token covers, *adding that token is part of the work*, not a follow-up.
- **Commit the whole handoff, runtime included.** Prototypes usually do not render without their
  runtime, and a handoff that cannot be opened is not a reference. Do not gitignore it. Do not edit
  it — it is the record of what was specified.
- **A handoff is a spec, not a plan.** It has no step order, it can contradict what the app actually
  does today, and it may quietly contain product decisions dressed as visual ones. It gets a
  planning pass before any of it is delegated, exactly like any other work.

## What the planning pass has to check

A design tool sees the screen. It does not see the system behind the screen. Every one of these has
been a real defect in a real handoff, and each is invisible unless someone looks for it:

- **Claims about behaviour that is not built.** One handoff justified a "Pause" button with "the
  session is already persisted per turn" — nothing was persisted at all. Verify every behavioural
  claim against the code, not against the handoff's confidence.
- **App-wide changes made while designing one screen.** Swapping a font family or a surface colour
  in the shared token layer restyles every screen, including the ones nobody designed. Decide
  explicitly whether the change is app-wide or scoped, and say which in the plan.
- **Unspecified variants.** Dark mode, large text scale, empty states, error states, and long-string
  overflow are routinely absent from a handoff. Each needs a decision recorded: design it, derive
  it, or gate it. Silence is not a decision.
- **Product decisions in visual clothing.** "Promote this out of the debug panel" changes what the
  app tells users about itself. That is a product call wearing a styling hat, and it needs the
  product owner, not an implementer.

Resolve these *before* implementation, and record the resolutions in the plan. When the plan departs
from the handoff, say so at the top of the handoff too, so the next reader does not implement the
superseded version.

## Stack specifics

Where the tokens actually live is the stack's business:

- Flutter — `flutter-toolkit:design-tokens`
- SwiftUI — `swiftui-toolkit:conventions`, "Design system"

Load the matching one before planning token work.
