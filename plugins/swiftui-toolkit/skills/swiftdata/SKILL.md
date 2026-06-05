# SwiftData

This skill covers optional SwiftData integration.

Guidelines:
- Keep SwiftData in a separate `SwiftData/` group so it can be removed if not needed.
- Define models in `SwiftData/Models/` and create `ModelContainer` in `SwiftData/AppModelContainer.swift`.
- Inject the model container in the app entry point and avoid direct `ModelContext` access in views.
- If using CloudKit, do not use `@Attribute(.unique)`, and make all relationship properties optional.
- Mark the module `[REMOVABLE]` in headers and plan docs if it is optional.
