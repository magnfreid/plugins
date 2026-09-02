---
description: Scaffold a new SwiftUI app laid out for this toolkit — target, groups, assets, string catalog, and the Core/ design-system skeleton.
---

# new-swiftui-app

Scaffold a new SwiftUI app, then seed its conventions so they are in force from the first commit.

Steps:

1. Create an Xcode App target with SwiftUI and Swift. **Ask for the deployment target** rather than
   assuming one — it is a product decision about which devices are supported, and a baseline
   asserted here becomes a rule nobody chose.
2. Replace the default `ContentView.swift` with the `Core/` skeleton: `DesignSystem/`, `Styles/`,
   `Components/`, `Services/`, plus `App/` and `Features/`.
3. Add all groups with **New Group with Folder**, so the folder tree on disk matches the project
   navigator.
4. Add `Assets.xcassets` with semantic colour sets, and a `Localizable.xcstrings` string catalog.
   Decide light-only versus light-and-dark **with the user** — a colour set with a dark variant
   nobody wanted is harder to remove later than to skip now.
5. Run `/swiftui-toolkit:init-conventions`. It writes the conventions into the new project's
   `CLAUDE.md` and copies the long-form blueprints into `.claude/reference/`, reading the build
   settings you just created rather than asserting defaults.

Step 5 is the one that matters. Everything above it is a folder tree; step 5 is what makes the
conventions apply on every future change without anyone having to remember them.
