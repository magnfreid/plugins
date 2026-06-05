# SwiftUI Architect

Use this agent guide when designing or evolving the SwiftUI app architecture.

Focus on:
- modern iOS 17+ SwiftUI patterns
- `@Observable` stores and environment injection
- a clean feature-first folder layout under `Features/`
- reusable `Core/Components/` and design tokens in `Core/DesignSystem/`
- optional SwiftData support that can be deleted without wide impact

Do not introduce new dependencies unless explicitly approved. Keep navigation centralized in `App/AppRouter.swift` and avoid view-level business logic.

See the `skills/` files for domain-specific conventions, and `agents/swiftui-architecture.md` for the full guidance rules.
