# Design System

This skill covers visual tokens and reusable styling patterns.

Guidelines:
- Define colors in `Assets.xcassets` and expose them as `Color.app*` in `Core/DesignSystem/Colors.swift`.
- Define typography styles in `Core/DesignSystem/Typography.swift` as `Font.app*` extensions.
- Define spacing constants in `Core/DesignSystem/Spacing.swift` and prefer them over literal values.
- Do not hardcode color, font, or spacing values inside views.
- Support light and dark mode using semantic color assets.
