# scaffold-feature

Scaffold a new SwiftUI feature using the toolkit conventions.

Steps:
1. Create a `Features/<FeatureName>/` folder.
2. Add all feature views inside the folder.
3. Add the new destination case to `App/AppRouter.swift`.
4. Add the destination handling in `Features/Root/MainTabView.swift` or the appropriate `NavigationStack`.
5. Add strings to `Resources/Localizable.xcstrings`.
6. Keep business logic in stores or services, not in views.
