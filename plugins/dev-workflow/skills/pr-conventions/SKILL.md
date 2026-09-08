---
name: pr-conventions
description: Branch naming, commit message style, pull request body structure, and the house voice for anything written into GitHub — PR bodies, review comments, inline comments, replies on someone else's PR. Use when creating a branch, writing a commit message, opening or updating a PR, or writing review feedback that will be posted — particularly inside the dev-workflow feature workflow.
---

# Branch, commit, and PR conventions

Defaults. A repository's own stated convention — CONTRIBUTING.md, a PR template, the existing
history — always wins. Check `git log --oneline -20` before assuming.

## Voice — anything posted to GitHub

Covers PR bodies, review summary comments, inline comments on a line, and replies on someone
else's PR. Write for a junior developer who does not have your context: they should finish reading
knowing what is wrong and what to do about it.

- **Be short.** A finding is two or three sentences. A body section is a short paragraph or a few
  bullets. Prose is fine, a wall of it is not. If a sentence would not change what the reader does,
  cut it.
- **Say the thing, then the fix.** What is wrong → what breaks because of it → what to do. In that
  order, with no preamble and no restating the diff back at the author.
- **Plain words.** Prefer the ordinary description over the pattern name: "the cached list still
  holds the deleted order" over "a coherence violation between the mutation and projection layers".
  Name a pattern only when the pattern is the point, and then say what it means in half a sentence.
- **Show rather than explain.** A two-line snippet of the fix beats a paragraph describing its
  shape.
- **Cut words, never facts.** The failure scenario, the `file:line`, the reason a check was not
  run, a deferred finding, an unpredictable edit — all of it stays however short the comment gets.
  If it cannot be both short and complete, be complete.
- **No filler.** No "great work overall", no severity theatre, no softening a real defect into
  vagueness to sound polite. Stating a problem plainly is not rude.

A finding in this voice:

> **`OrderRepository.dart:88` — the cached list is not updated after a delete.**
> `deleteOrder` removes the row from the database but leaves `_cachedOrders` untouched, so the list
> screen keeps showing the deleted order until the app restarts. Clear the cache in `deleteOrder`
> the way `addOrder` does on line 61.

What, what breaks, what to do — three sentences. Not: "Consider whether the caching strategy here
correctly maintains coherence with the persistence layer following mutation operations."

## Branches

`feature/<slug>`, `fix/<slug>`, `refactor/<slug>`, `chore/<slug>`, `docs/<slug>`, `test/<slug>` —
kebab-case, derived from the objective, no ticket numbers unless the repo uses them.

If the repo's history consistently uses a different prefix for the same thing — `feat/` rather than
`feature/` — match the repo. Consistency inside one history beats consistency across repositories.

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

At `--deep-review` there may be more than one of the second kind, one per reviewer. Name the lens rather
than numbering them — `fix(orders): address failure-mode review findings` — so the history says
what each round was answering.

Body only when the *why* is not obvious from the diff. No filler, no "as per the plan", no
generated-by trailers unless the repo already uses them.

## PR body

```markdown
## What
Two or three sentences: what changes for someone using the app, and why.

## Approach
The two or three decisions that shaped it, a bullet each. Anything that departs from convention
goes here with its reason. Link the plan if it is committed.

## Review
Automated review: N blocking, M non-blocking. Full findings in the comment thread.
- Fixed: <one line each>
- Deferred: <one line each, and why it can wait>

## Verification
Build: clean, from scratch — or: incremental, so no claim about warnings.
- [x] fvm dart analyze
- [x] fvm flutter test (48 passed)
- [ ] Manual: pagination on a slow connection — not automatable

## Notes
Only what a reviewer would not guess from the diff: out-of-scope problems noticed, follow-ups worth
filing, and **any edit no human made** — an SDK migrator, codegen output, a formatter pass, a bulk
find/replace across platform folders.
```

Drop a section that has nothing in it rather than writing "N/A".

Draft while unreviewed. Ready only once fixes have landed and the body reflects the final state.

## Rules

- Never claim a check passed that you did not run. An unchecked box is fine; a false one is not.
- **State which build backs the claim.** "No warnings" after an incremental build is not a result —
  the compiler said nothing about the files it did not recompile. Either build from scratch or say
  the run was incremental and make no claim about warnings.
- Deferred findings go in the body, not only in the comment thread — the thread disappears on a
  squash merge.
- Never open a PR from a broken build.
- The title is the commit convention, not a sentence: `feat(orders): paginate order history`.
- **Call out anything a reviewer would not predict from the title.** Auto-migrated config,
  regenerated files, a rename that swept platform folders, a dependency bump that came along for
  the ride. Surprises in a diff are what make review expensive — a named surprise costs a
  sentence, an unnamed one costs an hour.
- **Never force-push a branch under review.** Push follow-up commits instead. Rewriting history
  under a reviewer invalidates every comment anchored to it and hides what changed between passes.
- A project's own instruction to "stop after opening the PR" means *do not merge*. It does not
  forbid the review and fix steps — those happen on the PR, which is exactly where the project
  wanted them.
