# Components

This skill covers reusable UI style patterns for the SwiftUI toolkit.

Guidelines:
- Prefer reusable styles and modifiers for built-in controls, such as `ButtonStyle`, `TextFieldStyle`, `LabelStyle`, and custom `ViewModifier`s.
- Keep visual tokens in `Core/DesignSystem/` and style definitions in `Core/Styles/`.
- Use wrapper views in `Core/Components/` only when the UI requires repeated structure or composition beyond styling.
- When creating wrappers, prefix component types with `App`, e.g. `AppDivider`, `AppSectionHeader`.
- Accept `LocalizedStringKey` for any user-facing text.
- Keep components and styles focused on presentation and avoid embedding business logic.
- Ensure the UI supports both light and dark mode using semantic colors.
