# Logging

*Project reference, seeded from `swiftui-toolkit`. This project owns it — edit it here.*

Guidelines:
- Use `Logger` from `OSLog` instead of `print()`.
- Define reusable `Logger` categories in `Services/LoggingService.swift`.
- Use privacy annotations for sensitive values: `.private` or `.sensitive`.
- Use the appropriate log level: `debug`, `info`, `warning`, `error`, `critical`.
- **Never log personal data unredacted.** `OSLog` interpolation is `.private` by default for
  non-numeric values, but numbers and booleans are public — annotate explicitly rather than relying
  on the default, and use `.sensitive` for anything regulated.
