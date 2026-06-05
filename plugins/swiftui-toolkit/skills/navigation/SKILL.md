# Navigation

This skill covers the toolkit's navigation architecture.

Guidelines:
- Use `NavigationStack` and `navigationDestination(for:)`.
- Centralize programmatic navigation in `AppRouter`.
- Use `@Bindable var router = router` in views that bind to the router path.
- Do not use `NavigationLink(destination:)` for programmatic navigation; use the router instead.
- Keep navigation logic declarative and avoid prop-drilling the router by environment-injecting it.
