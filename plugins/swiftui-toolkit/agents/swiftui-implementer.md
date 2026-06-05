# SwiftUI Implementer

Use this agent guide when writing SwiftUI screens, stores, services, and shared components.

Key principles:
- Use `@State` for local screen state and `@Environment(StoreName.self)` for shared stores.
- Never use `ObservableObject`, `@Published`, `@StateObject`, `@ObservedObject`, or `@EnvironmentObject`.
- Use semantic color, font, and spacing tokens from `Core/DesignSystem/`.
- Keep components pure UI and accept `LocalizedStringKey` for text.
- Use `NavigationStack` with `navigationDestination(for:)` and programmatic navigation through `AppRouter`.

If a screen needs complex local logic, add a view-specific `@Observable` view model and inject it via `.environment()`.
