---
name: swiftui-test-writer
description: Guidance for writing unit and view tests for SwiftUI projects using the toolkit.
tools: Read, Grep, Glob
model: haiku
---

# SwiftUI Test Writer

Use this guide when adding unit tests or view tests for the SwiftUI toolkit.

Testing guidance:
- Prefer unit tests for stores, services, and business logic.
- Use `@MainActor` for tests that touch `@Observable` state.
- Avoid UI tests unless the app needs cross-screen behavior that cannot be validated with unit tests.
- Keep view tests small and focused on view state and binding behavior.
- If SwiftData is involved, test service-level persistence logic rather than direct view interaction.

Use the repository conventions for naming and place tests in a separate test target where available.

# SwiftUI Test Writer

Use this guide when adding unit tests or view tests for the SwiftUI toolkit.

Testing guidance:
- Prefer unit tests for stores, services, and business logic.
- Use `@MainActor` for tests that touch `@Observable` state.
- Avoid UI tests unless the app needs cross-screen behavior that cannot be validated with unit tests.
- Keep view tests small and focused on view state and binding behavior.
- If SwiftData is involved, test service-level persistence logic rather than direct view interaction.

Use the repository conventions for naming and place tests in a separate test target where available.
