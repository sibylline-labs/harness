# Mocking and Seams

Load before creating any mock, fake, or patch — or when a test's setup is growing past its assertions.

## Where mocks are allowed

Mock at **system boundaries** only — the places where the process ends and the world begins:

- External providers (payment, email, chain RPCs, partner APIs)
- Time and randomness
- The network

Leave real (or use a fake/test instance of):

- Your own classes, services, and modules
- Internal collaborators — anything you control
- The database, where a real test DB or in-memory fake exists (persistence invariants belong in the DB lane, not in query-choreography mocks)

The tell you've mocked an internal: the test breaks when you refactor call structure and behavior hasn't changed.

## Fakes over mock graphs

A test wiring five-plus mocks has rebuilt the implementation's topology inside the test — it chooses every response, makes the implementation inevitable, and goes red on refactors instead of on bugs. A suite audit found hundreds of these; they are the single largest maintenance drag.

Replace the graph with **one stable fake per boundary**:

- An in-memory repository that records domain entities — assert what was persisted, not which ORM methods ran.
- A workflow harness faking `run`/`sleep`/external calls — assert emitted step outcomes and durable state.
- A provider fake returning canned, **complete** responses.

One behavioural scenario against fakes replaces several call-pinning tests. Keep an interaction assertion only where the call is the contract (money movement, event publication, exactly-once) — and then assert *that* call narrowly, not the whole choreography.

## Keeping mocks honest

- **Complete shapes.** A mock response mirrors the real payload in full — every field the real API returns — not just the fields this test reads. Partial mocks pass locally and fail in integration when downstream code reads an omitted field. If you can't state the full shape, you don't understand the boundary well enough to mock it; go read the real response first.
- **Understand before replacing.** Before mocking a method, know its side effects and whether this test depends on one of them. Mocking "to be safe" is how a test silently stops exercising the thing it names. Unsure? Run the test against the real implementation once, observe what it needs, then mock minimally at the lower level.
- **Design boundaries for mockability.** Inject dependencies rather than constructing them inside; prefer SDK-style per-operation interfaces (`api.getUser(id)`) over generic fetchers, so each fake returns one shape with no conditional logic.
- **Test utilities live in test code.** Cleanup/teardown helpers go in `tests/` utilities — never as methods on production classes whose only caller is a test.

## Warning signs

- Mock setup longer than the assertions it serves
- A mock missing methods/fields the real object has
- The mock's return value asserted back (testing the mock)
- Patching a symbol you own two files away instead of injecting at the boundary
- "I'll mock this to be safe"

Each points the same way: move to the seam, fake the boundary, assert the outcome.
