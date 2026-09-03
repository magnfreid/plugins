---
name: logging
description: How to log in Swift with OSLog — Logger categories, privacy annotations for sensitive values, and choosing a level. Use when adding logging, or replacing print statements, in Swift.
---

# Logging with OSLog

How to log once a project is logging through OSLog.

**Technique, not choice.** This is how to work with OSLog once the project has decided to
use it. Whether to use it at all, where the files live, and what things are called are the
project's decisions — its `CLAUDE.md` and the patterns already in the code win over anything
here, and they win without discussion. Nothing in this file is a reason to restructure a repo.

## Rules

- Use `Logger` from `OSLog` rather than `print()`. `print` does not reach the unified log, so it is
  invisible on a device and in a sysdiagnose — the two places you actually need it.
- Define reusable `Logger` categories once, in whatever file the project keeps its services in, and
  reuse them. A `Logger` constructed at a call site loses the subsystem/category filtering that
  makes the log readable.
- Pick the level deliberately: `debug`, `info`, `warning`, `error`, `critical`. `debug` is stripped
  from release builds; anything you need in a field report must be `info` or above.
- **Never log personal data unredacted.** `OSLog` interpolation is `.private` by default for
  non-numeric values, **but numbers and booleans are public** — annotate those explicitly rather
  than relying on the default. Use `.sensitive` for anything regulated.

That default is the part worth remembering: an ID logged as a `String` is redacted, and the same ID
logged as an `Int` is not. Nothing warns you.
