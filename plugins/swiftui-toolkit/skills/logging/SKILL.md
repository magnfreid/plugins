# Logging

This skill covers logging conventions for the SwiftUI toolkit.

Guidelines:
- Use `Logger` from `OSLog` instead of `print()`.
- Define reusable `Logger` categories in `Services/LoggingService.swift`.
- Use privacy annotations for sensitive values: `.private` or `.sensitive`.
- Use the appropriate log level: `debug`, `info`, `warning`, `error`, `critical`.
