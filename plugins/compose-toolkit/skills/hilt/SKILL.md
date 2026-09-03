---
name: hilt
description: How to wire Hilt on Android — constructor injection, @Binds modules for interface-to-implementation, @HiltViewModel and hiltViewModel(), scoping, and injecting dispatchers with a qualifier so they can be replaced in tests. Use when adding a dependency-injection binding, a module, or an injectable type.
---

# Wiring Hilt

How to bind and inject once a project is using Hilt.

**Technique, not choice.** This is how to work with Hilt once the project has decided to use it.
Whether to use it at all, where the files live, and what things are called are the project's
decisions — its `CLAUDE.md` and the patterns already in the code win over anything here, and they
win without discussion. Nothing in this file is a reason to restructure a repo.

## Constructor injection first

Anywhere it is possible. A type with an `@Inject constructor` needs no module at all — modules are
for types you do not own, and for binding an interface to an implementation.

## Binding an interface

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    abstract fun bindAuthRepository(impl: DefaultAuthRepository): AuthRepository
}
```

`@Binds` over `@Provides` for this shape — it generates less code and cannot accidentally
construct. Keep the binding module the **only** place a concrete implementation is named; that is
what makes the implementation swappable without touching call sites.

## ViewModels

`@HiltViewModel` on the class, `hiltViewModel()` at the screen's stateful overload. Nowhere else —
calling it deeper in the tree scopes the ViewModel to the wrong thing.

With Navigation 3, `NavDisplay` must be given `entryDecorators` including
`rememberViewModelStoreNavEntryDecorator()`, or ViewModels are not scoped to their nav entry. This
is the single most common Nav3 mistake, and the symptom is a ViewModel that survives when it should
not, or dies when it should not.

## Scoping

Scope only what needs it: shared mutable state, or something expensive to build. An unscoped
binding is cheaper and has no lifetime to reason about. `@Singleton` on a stateless mapper buys
nothing and costs a graph entry.

## Dispatchers

Inject them with a qualifier:

```kotlin
@Qualifier @Retention(AnnotationRetention.BINARY) annotation class IoDispatcher

class DefaultProductRepository @Inject constructor(
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher,
)
```

**Never hardcode `Dispatchers.IO` inside a repository.** It cannot be replaced in a test, so every
test of that repository ends up either slow or flaky, and nothing tells you which.

## Test doubles

A `Fake*` shipped beside a repository in `main/` — for previews and for UI work that should not
need a network — must **never** be bound in a production module. R8 strips it when nothing in the
release graph references it; a stray `@Binds` is what keeps it in the APK.
