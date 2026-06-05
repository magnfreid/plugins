# Localization

This skill covers string localization for the SwiftUI toolkit.

Guidelines:
- Use `LocalizedStringKey` for all user-visible text.
- Add keys to `Resources/Localizable.xcstrings` using dot notation, e.g. `login.email.placeholder`.
- Do not hardcode English text in views.
- Prefer centralized string keys rather than repeated literal strings.
- When available, use symbol-based localization accessors in Xcode if the project supports them.
