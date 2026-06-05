# SwiftUI Refactor

Use this agent guide when converting existing SwiftUI code to the toolkit architecture.

Refactor checklist:
- Move all views into `Features/<FeatureName>/` groups.
- Replace `ObservableObject` and `@Published` with `@Observable` stores and environment injection.
- Move shared state to `Stores/` and inject with `.environment(...)`.
- Convert `NavigationView` to `NavigationStack` and centralize deep navigation in `AppRouter`.
- Convert hardcoded strings to `LocalizedStringKey` and add them to `Resources/Localizable.xcstrings`.
- Use `Color.app*`, `Font.app*`, and `Spacing.*` instead of raw values.

Keep UI code thin and ask whether behavior belongs in a store or service before adding it to a view.
