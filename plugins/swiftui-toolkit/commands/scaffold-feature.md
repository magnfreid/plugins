---
description: Scaffold a new SwiftUI feature folder, register its route on AppRouter, and wire its strings.
---

# scaffold-feature

Scaffold a new SwiftUI feature. The conventions this follows are the ones in the project's own
`CLAUDE.md` — read them first; this command is the mechanical part, not the authority.

Steps:

1. Create a `Features/<FeatureName>/` folder.
2. Add the feature's views inside it, plus its `@Observable` store if the screen has non-trivial
   local logic.
3. Add the new destination case to `App/AppRouter.swift`.
4. Handle the destination in `Features/Root/MainTabView.swift`, or whichever `NavigationStack`
   owns it.
5. Add the feature's strings to the project's string catalog. No user-facing literal in a view.
6. Keep business logic in the store or a service, never in a `body`.

If the project's `CLAUDE.md` has no SwiftUI conventions block yet, run
`/swiftui-toolkit:init-conventions` first — otherwise this scaffolds against defaults nobody wrote
down, which is the drift this toolkit exists to prevent.
