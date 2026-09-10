---
name: pr-conventions
description: Branch naming, commit message style, pull request body structure, and the house voice for anything written into GitHub — PR bodies, review comments, inline comments, replies on someone else's PR — and for comments in source files. Use when creating a branch, writing a commit message, opening or updating a PR, writing review feedback that will be posted, or writing a comment in code.
---

# Branch, commit, and PR conventions

Defaults. A repository's own **stated** convention wins — CONTRIBUTING.md, a CLAUDE.md, a PR
template, a commit prefix its history uses consistently. Check `git log --oneline -20` and the
template before assuming.

That deference is about **structure and format only**: which sections a body has, `feat/` versus
`feature/`, whether ticket numbers appear. **Never infer length or register from what is already
there.** The voice rules below are absolute, and a repository whose existing PR bodies, review
comments or code comments are long is not setting a bar to match — matching it is how a verbose
first PR becomes a verbose fiftieth. Write to the rules, not to the neighbours.

## Voice — anything posted to GitHub, and comments in code

Covers PR bodies, review summary comments, inline comments on a line, replies on someone else's
PR, commit messages, and comments in source files. Write for a junior developer who does not have
your context: they should finish reading knowing what is wrong and what to do about it.

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

### Do not narrate how the change got here

The reader is looking at the change in front of them, not its history. This applies to PR bodies
and review replies as much as to code.

- No recap of what an earlier PR did, what a review round changed, what was tried first, or why the
  branch was rebased — unless the reader needs it to review *this* diff.
- No defending the change against alternatives nobody proposed. "Why this way" earns a sentence
  when it is genuinely non-obvious or departs from a convention, and nothing otherwise.
- No process: no plans, no agents, no step numbers, no "as per the plan".
- Superseded decisions live in the ADR or the commit that made them. Point at it; do not retell it.

### Comments in source files

A comment explains something the reader needs **now**, that the code cannot say itself: a
non-obvious constraint, an ordering that matters, a workaround for behaviour outside your control.

- Never explain a line by what it used to be, what it replaced, or which PR or review changed it.
  That is what `git log` is for, and the comment goes stale the moment the code moves on.
- Cite a decision record only where breaking the rule is a live temptation — not on every line the
  record touched. One pointer beats five.
- "X rather than Y" is worth writing only when someone would reach for Y and be wrong. Otherwise
  describe X.
- No comment beats a comment restating the code.

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

**A commit message describes the change, not how it was produced.** No plans, no reviews, no
agents, no step numbers, no "as per the plan", no generated-by trailers unless the repo already
uses them. Someone reading `git log` in six months wants to know what moved, and the process that
moved it is not part of the answer.

One commit per workflow run. Implementation and the fixes from the workflow's own review land
together — that review is a step inside building the change, not a change to it, so it does not
earn a line in the history.

After the handoff, each round of changes Magnus asks for gets its own commit, named for what
changed:

```
fix(orders): keep the cursor when the list refreshes
```

Body only when the *why* is not obvious from the diff.

## PR body

Magnus opens the pull request, by hand, when the branch is worth the team's time. Keep the body
about the change — a reviewer wants to know what it does and what to look at, not what process
produced it.

```markdown
## What
Two or three sentences: what changes for someone using the app, and why.

## Approach
The two or three decisions that shaped it, a bullet each. Anything that departs from convention
goes here with its reason.

## Verification
Build: clean, from scratch — or: incremental, so no claim about warnings.
- [x] fvm dart analyze
- [x] fvm flutter test (48 passed)
- [ ] Manual: pagination on a slow connection — not automatable

## Notes
Only what a reviewer would not guess from the diff: a known gap left in on purpose, a follow-up
worth filing, and **any edit no human made** — an SDK migrator, codegen output, a formatter pass,
a bulk find/replace across platform folders.
```

Drop a section that has nothing in it rather than writing "N/A". Four short sections beat four
long ones; a body nobody finishes reading is a body that hid something.

## Rules

- Never claim a check passed that you did not run. An unchecked box is fine; a false one is not.
- **State which build backs the claim.** "No warnings" after an incremental build is not a result —
  the compiler said nothing about the files it did not recompile. Either build from scratch or say
  the run was incremental and make no claim about warnings.
- Never open a PR from a broken build.
- The title is the commit convention, not a sentence: `feat(orders): paginate order history`.
- **Call out anything a reviewer would not predict from the title.** Auto-migrated config,
  regenerated files, a rename that swept platform folders, a dependency bump that came along for
  the ride. Surprises in a diff are what make review expensive — a named surprise costs a
  sentence, an unnamed one costs an hour.
- **Never force-push a branch under review.** Push follow-up commits instead. Rewriting history
  under a reviewer invalidates every comment anchored to it and hides what changed between passes.
