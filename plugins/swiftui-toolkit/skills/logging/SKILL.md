---
name: logging
description: Logging in SwiftUI projects with OSLog — Logger categories, privacy annotations for sensitive values, and choosing a log level. Trigger on logging, print statements, OSLog, Logger, or debugging output in Swift code.
---

# Logging

Guidelines:
- Use `Logger` from `OSLog` instead of `print()`.
- Define reusable `Logger` categories in `Services/LoggingService.swift`.
- Use privacy annotations for sensitive values: `.private` or `.sensitive`.
- Use the appropriate log level: `debug`, `info`, `warning`, `error`, `critical`.
- **Never log personal data unredacted.** `OSLog` interpolation is `.private` by default for
  non-numeric values, but numbers and booleans are public — annotate explicitly rather than relying
  on the default, and use `.sensitive` for anything regulated.
