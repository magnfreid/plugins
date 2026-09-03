---
name: design-tokens
description: How to build reusable SwiftUI styling — semantic colours in an asset catalog, Font and Spacing extensions, ButtonStyle and ViewModifier, and wrapper views over system controls. Use when changing colours, typography, or spacing, styling a control, or implementing a design in SwiftUI.
---

# SwiftUI tokens and styling

How to add and consume styling values, once a project has decided where its design system lives.

**Technique, not choice.** This is how to work with a SwiftUI design system once the project has decided to
use it. Whether to use it at all, where the files live, and what things are called are the
project's decisions — its `CLAUDE.md` and the patterns already in the code win over anything
here, and they win without discussion. Nothing in this file is a reason to restructure a repo.


## Where things live

```
Core/
  DesignSystem/
    Colors.swift       Color.app* — thin accessors over semantic colour sets
    Typography.swift   Font.app* extensions
    Spacing.swift      named spacing constants
  Styles/              ButtonStyle, TextFieldStyle, LabelStyle, ViewModifier
  Components/          wrapper views, prefixed App* (AppDivider, AppSectionHeader)
```

**Colours are defined as semantic colour sets in `Assets.xcassets`**, with light and dark variants
supplied by the asset, and exposed as `Color.app*` accessors. That is what makes dark mode a
property of the asset rather than a branch in every view.

## Style before wrapper

Reach for a **style or modifier** on a built-in control first — `ButtonStyle`, `TextFieldStyle`,
`LabelStyle`, a custom `ViewModifier`. A `Button` with a project style keeps every behaviour,
accessibility trait, and platform affordance Apple ships.

Add a **wrapper view in `Core/Components/`** only when the UI needs repeated *structure* — composition
beyond styling. Wrapping a control to restyle it trades away behaviour you did not mean to give up.

Wrappers take `LocalizedStringKey` for user-facing text, stay presentation-only, and carry no
business logic.

## Adding a token

When a design introduces a value nothing covers, **adding the token is part of that work** — not a
follow-up. Inline the literal and the literal is what ships, and the next screen copies it.

Name for role, not appearance: `Color.appBubbleUser`, not `Color.appSage`. A recoloured design then
costs one asset edit rather than a find-and-replace across features.

## Rules

- No literal `Color(...)`, `.font(.system(size:))`, or hardcoded padding in a feature view.
- Never UIKit colours in SwiftUI code.
- Do not force font sizes — use Dynamic Type. A design's point sizes map onto text styles.
- Light and dark both come from semantic assets. Do not branch on `colorScheme` to pick a colour.
- Implementing a design handoff? Load `dev-workflow:design-handoff` first — it covers what to verify
  in the handoff before any of this matters.
