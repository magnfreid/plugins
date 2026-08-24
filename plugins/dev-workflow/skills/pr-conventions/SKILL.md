---
name: pr-conventions
description: Branch naming, commit message style, and pull request body structure for Magnus's repositories. Use when creating a branch, writing a commit message, or opening or updating a PR — particularly inside the dev-workflow feature workflow.
---

# Branch, commit, and PR conventions

Defaults. A repository's own stated convention — CONTRIBUTING.md, a PR template, the existing
history — always wins. Check `git log --oneline -20` before assuming.

## Branches

`feature/<slug>`, `fix/<slug>`, `refactor/<slug>`, `chore/<slug>` — kebab-case, derived from the
objective, no ticket numbers unless the repo uses them.

Always branch from an up-to-date base. Never commit to the default branch.

## Commits

Conventional Commits: `type(scope): summary` in the imperative, under 72 characters.

```
feat(orders): paginate order history
fix(auth): read currentUser inside the redirect callback
```

Two commits per workflow run, kept separate on purpose:

1. The implementation.
2. `fix(<scope>): address review findings` — so the PR history shows what the review changed.

Body only when the *why* is not obvious from the diff. No filler, no "as per the plan", no
generated-by trailers unless the repo already uses them.

## PR body

```markdown
## What
One paragraph. What this changes and why, in terms of behaviour rather than files.

## Approach
The two or three decisions that shaped the implementation. Link the plan if it is committed.
Anything that departs from convention goes here with its reason.

## Review
Automated review: N blocking, M non-blocking. Full findings in the comment thread.
- Fixed: <one line each>
- Deferred: <one line each, with why>

## Verification
- [x] fvm dart analyze
- [x] fvm flutter test (48 passed)
- [ ] Manual: pagination on a slow connection — not automatable

## Notes
Anything a reviewer should know: out-of-scope problems noticed, follow-ups worth filing.
```

Draft while unreviewed. Ready only once fixes have landed and the body reflects the final state.

## Rules

- Never claim a check passed that you did not run. An unchecked box is fine; a false one is not.
- Deferred findings go in the body, not only in the comment thread — the thread disappears on a
  squash merge.
- Never open a PR from a broken build.
- The title is the commit convention, not a sentence: `feat(orders): paginate order history`.
