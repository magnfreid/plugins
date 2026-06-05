# State Management

This skill covers shared and local state in the SwiftUI toolkit.

Guidelines:
- Use `@Observable` for shared stores in `Stores/`.
- Instantiate stores in the app entry point with `@State` and inject them with `.environment()`.
- Read stores in views with `@Environment(StoreName.self)`.
- Use `@State` only for local view state.
- Do not use singletons for stores.
- Add view-specific `@Observable` view models only when a view has complex logic that does not belong in a shared store.
