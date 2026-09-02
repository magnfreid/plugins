# Testing

*Project reference, seeded from `swiftui-toolkit`. This project owns it — edit it here.*

**Doctrine — what to test, why tests ship with the code, and what a "silent seam" is — lives in
`dev-workflow:testing-doctrine`.** Load it if it is not loaded. This file is the Swift half.

## Framework

**Swift Testing** (`import Testing`) for new tests: `@Test`, `#expect`, `#require`, `@Suite`.
XCTest remains for `XCUITest` UI tests and for suites that already exist — do not convert a working
XCTest suite as a side effect of another change.

```swift
import Testing
@testable import MyApp

@MainActor
@Suite("SessionStore")
struct SessionStoreTests {
    @Test("signing in publishes the authenticated user")
    func signInPublishesUser() async throws {
        let auth = FakeAuthService(result: .success(.stub))
        let store = SessionStore(auth: auth)

        await store.signIn(email: "a@b.com", password: "pw")

        #expect(store.state == .authenticated(.stub))
    }
}
```

## @MainActor

`@Observable` types that drive UI are `@MainActor`, so their tests are too — annotate the suite, not
each test. A test that touches main-actor state from a background context will either fail to
compile under strict concurrency or, worse, pass while racing.

Do not sprinkle `await MainActor.run { }` inside tests to dodge the annotation. That hides exactly
the isolation problem the test should be surfacing.

## Fakes, not mocks

Services sit behind a protocol; the fake is a real type in the test target (or shipped alongside the
protocol when UI work needs it):

```swift
struct FakeAuthService: AuthService {
    var result: Result<User, AuthError>
    func signIn(email: String, password: String) async throws -> User { try result.get() }
}
```

No mocking framework. If faking a dependency is awkward, the protocol is usually the problem — say
so rather than reaching for a library.

## What gets a test

Per the doctrine, mapped onto this stack:

- **Required:** `@Observable` stores and view models (happy path *and* error path), every service's
  public contract including how it maps failures, and pure domain logic.
- **Required:** the silent seams — `Codable` round-trips, cache-versus-network read paths, and error
  mapping where a typed failure can be flattened into a generic one.
- **Default:** one test per screen that builds the real view with its environment injected. It
  proves the screen composes; a view assembled by hand from its subviews does not.
- **Not required:** purely presentational views.

## UI tests

`XCUITest` only for cross-screen behaviour a unit test cannot reach — a full sign-in flow, a
navigation path that spans several screens. They are slow and flaky in proportion to how much they
cover, so they earn their place one at a time.

If SwiftData is involved, test the service-level persistence logic, not the view that displays it.

## Anti-patterns

- **Testing through the view when the logic is in a store.** Move the logic, then test the store.
- **`Task.sleep` to wait for state.** Await the operation, or expose something to await. A sleep is
  a race with a timer attached.
- **Shared mutable fixtures across tests** — fresh instances per test.
- **Asserting the general shape of an error** (`#expect(throws: AppError.self)`) where a catch-all
  can produce the same type. Assert the case that distinguishes it.
