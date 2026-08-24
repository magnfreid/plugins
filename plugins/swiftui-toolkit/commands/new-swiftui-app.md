---
description: Scaffold a new SwiftUI app laid out for this toolkit — target, groups, assets, string catalog, and the Core/ design-system skeleton.
---

# new-swiftui-app

Scaffold a new SwiftUI app using this toolkit's conventions.

Steps:
1. Create an Xcode App target with SwiftUI and Swift. Set the deployment target to the toolkit baseline, **iOS 26.0** — lower it only if the project has a stated reason, and record that reason.
2. Delete default ContentView.swift and replace with files from `swiftui-toolkit`.
3. Add all groups with 'New Group with Folder'.
4. Add `Assets.xcassets` with semantic colour sets and `Resources/Localizable.xcstrings`, per `swiftui-toolkit:design-tokens` and the Localization section of `swiftui-toolkit:conventions`.
