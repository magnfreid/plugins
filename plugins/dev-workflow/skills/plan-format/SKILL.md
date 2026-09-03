---
name: plan-format
description: The contract for an implementation plan that a Sonnet agent can execute without making design decisions. Use when writing, reviewing, or repairing a plan produced by the dev-workflow feature workflow, or whenever asked to "write a plan for" a code change that another agent will implement.
---

# Plan format

A plan is not a description of a feature. It is a set of instructions precise enough that an
implementer can follow it without deciding anything. Every decision left open is a decision the
implementer will make badly, silently, and in a way that matches its training data rather than
this codebase.

The test for a finished plan: **could an agent that has never seen this repo execute it correctly
by reading only the plan and the files the plan names?** If no, the plan is not done.

## Non-negotiables

1. **Ground it in the repo first.** Read the files you are about to modify. Grep for an existing
   feature of the same shape and mirror it. A plan written from the prompt alone is a guess.
2. **Name every file.** Repo-relative paths. Say created / modified / deleted / generated.
3. **Give signatures, not prose.** Class names, constructor parameters, method signatures, event
   and state shapes. No bodies.
4. **Order the steps.** Generated code before the code that imports it, domain before UI,
   contracts before consumers.
5. **State what NOT to do.** Grounded in this repo, not generic advice. See below — this is the
   section people skip and it is the one that prevents the most damage.
6. **Be terse.** A small feature gets a short plan. Padding a plan to look thorough makes it
   harder to follow, not safer.

## Required sections

Write them in this order, with these headings.

### 1. Objective
Two or three sentences. What is being built and what it is explicitly not. If the brief contained
an ambiguity you resolved, say which way you resolved it and why.

### 2. Conventions applied
A short table of the binding choices and where each came from. This exists so drift is visible at
review time, when it is still cheap to correct.

| Choice | Value | Source |
|---|---|---|
| State management | BLoC + Freezed unions | CLAUDE.md |
| HTTP | Dio via `packages/api_client` | existing code in repo |

If you deliberately depart from a convention, it goes in this table with source `deviation` and a
one-line reason. Never depart silently.

### 3. Files
Flat list, repo-relative, one line of responsibility each.

```
lib/features/orders/order_bloc.dart          (create)   order list state machine
lib/features/orders/order_bloc.freezed.dart  (generated)
packages/orders_api/lib/src/order_dto.dart   (create)   wire model
lib/router/routes.dart                       (modify)   add /orders route
```

### 4. Contracts
Public surface only, for every non-trivial type. For state machines, the full event and state
unions — this is where implementers improvise most, so leave them nothing to improvise.

### 5. Steps
Numbered. Each step is one coherent unit of work with a named outcome. If a step requires a
decision the implementer would have to make, the plan is incomplete — make the decision here.
Include the codegen and verification commands as their own steps.

### 6. Guard rails
The section that earns the plan its keep. Concrete and repo-specific:

- **Do not** touch files outside the list in section 3. If a change seems needed elsewhere, stop
  and report instead.
- **Do not** add a dependency. If one seems necessary, stop and report.
- **Do not** redesign. If the plan is wrong, say so and stop — a wrong plan executed faithfully is
  recoverable, a plan quietly rewritten mid-flight is not.
- Known traps in *this* code — the thing that looks right and isn't. Name them individually,
  e.g. "`AuthRepository.currentUser` is nullable during app start; read it inside the redirect
  callback, not at router construction."
- Anything that must not regress: existing tests, a public API, a serialized format.

### 7. Verification
The exact commands that must pass before the work is considered done, in order. Analyzer, codegen,
tests, build. Plus anything only a human can check, listed separately and honestly labelled as
not-automatable.

### 8. Open questions
Things you could not decide without input. If there are none, write `None.` Do not manufacture
questions to look careful. Anything in this section blocks the gate — the plan is not approvable
until it is empty.

## Anti-patterns

| Symptom | Why it fails |
|---|---|
| "Implement the repository pattern here" | Names a pattern, not a file or a signature. The implementer invents both. |
| "Handle errors appropriately" | Unfalsifiable. Say which errors, caught where, surfaced how. |
| "Add tests" | Say which behaviours, in which file, with which fakes. |
| A plan longer than the diff it produces | You are writing the code in prose. Give contracts and stop. |
| Guard rails that are generic best practice | "Write clean code" guards nothing. Guard rails must be things that would actually go wrong here. |
