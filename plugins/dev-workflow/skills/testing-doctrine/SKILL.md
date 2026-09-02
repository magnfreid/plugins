---
name: testing-doctrine
description: What to test and why, independent of language or framework — tests ship with the code they cover, which seams have to be pinned because they break silently, and why full coverage is not the goal. Load when deciding what coverage a change needs, or when a stack's own testing skill defers to it.
---

# Testing doctrine

Stack-agnostic. The *patterns* — `bloc_test`, XCTest, whatever the stack uses — belong to the
project, wherever it keeps them. This is the part that does not change when the language does.

**The binding half of this belongs in the project's `CLAUDE.md`,** not here. "Tests ship in the
same PR" is a rule that must hold whether or not anything loaded, and a skill only applies if it
triggers. This file is the reasoning behind the rule, and the part you consult while deciding what
a specific change needs. **Where the project says something different, the project wins** — that
holds however its rules got there, hand-written or seeded.

## Tests ship in the same PR as the code they cover

Not a follow-up, not a later pass, not "once it stabilizes."

This reverses a "skip tests unless asked" default these plugins used to carry. It was dropped after
a feature shipped a crash-on-open to a real device — nothing in the repo mounted a screen, so
nothing caught it. The rule keeps its scar attached deliberately: a rule with no cost attached is
one that gets quietly re-litigated the next time tests feel expensive.

## What must be covered

Three tiers. Map them onto whatever the stack calls these things.

**Required** — a change adding any of these is not done without tests:

- **Every new unit of state** — a BLoC, a Cubit, an `@Observable` store, a view model. The happy
  transitions *and* the error paths.
- **Every public contract of a repository or service**, including how it maps failures.
- **Pure domain logic** — anything with branches and no UI framework import.
- **Any seam that breaks silently.** See below.

**Default** — one test per screen that opens it the way the app does, plus the screen's primary
interaction where it has one.

**Not required** — purely presentational components, and generated code.

## Silent seams

The reason to test something is rarely that it is complicated. It is that **breaking it produces no
error**: the suite stays green, the compiler says nothing, and the damage surfaces later as
behaviour nobody can trace back to a diff.

The canonical instance is **exception-handling order**. A wrapper that rethrows a typed failure
before a catch-all is order-dependent, and swapping the two clauses silently downgrades every typed
failure to "unknown." Others of the same shape:

- **Serialization round-trips** — a renamed field still compiles and still writes.
- **Cache-versus-source read paths**, where the wrong one returns plausible stale data.
- **Precedence and ordering rules** generally: redirect chains, interceptor order, merge strategies,
  which config wins.

For each, the test must **fail when the order is wrong** — which usually means asserting the
discriminating detail rather than the general shape. An assertion that passes under both the correct
and the broken arrangement has pinned nothing, and is worse than no test at all: the gap is now
invisible, and it looks like coverage on a report.

## Test through the real composition, not a substitute for it

Wiring is where lifecycle bugs live — providers, injection, initialization order, what gets built
when a screen opens. A test that hand-assembles a screen from its parts with every dependency
replaced proves the parts render. It cannot prove the screen opens.

So the default screen test drives the **real** entry point and substitutes further down: the
repositories, the network, the clock. Replacing the state object itself answers a different
question — how a specific state renders — and is a second test, not a cheaper version of the first.

## Full coverage is not the goal

Cover the seams whose breakage is silent, and the paths a user actually walks. That is the entire
target.

Skipping something genuinely churny is fine — say so in the PR's open items. An acknowledged gap is
visible and can be argued with. A test nobody trusts is neither.

## Rules

- **Never change the implementation to make a test pass.** If the implementation looks wrong, say so
  and stop. That is a finding, not an obstacle.
- **Never claim a check passed that you did not run.**
- **No shared mutable state between tests.** Fresh fixtures per test — order-dependent suites fail
  in ways that get blamed on the wrong change.
- **A test that asserts nothing is not a test.** Driving code with no assertion proves only that it
  did not throw today.
