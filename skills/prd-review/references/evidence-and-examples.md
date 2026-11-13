# Worked Examples (`prd-review`)

Anonymised patterns from executed PRDs. Each pairs a step of `prd-review` with a PRD that did it
and a PRD that skipped it.

## 1. Observed substrate vs. inferred premise (Step 1)

- **Good:** before locking, the author probed eight live partner profiles and three live stores,
  and found that the checkout call needed a nested `checkout: { cart_id, line_items: [] }` body
  and a mandatory country field, both of which the partner's prose docs contradicted. Zero
  architectural redesigns followed.
- **Good:** the codebase baseline was hand-counted in `## Context` ("7 captured tables, 18
  transition rules, ~55 save points") and every lint finding listed its exact today-count.
- **Failure:** a PRD locked "verifiable against the wallet contract" and "unify on the chain's
  signature precompile" without an on-chain probe. One `eth_call` later showed the address was a
  shared singleton and the precompile used an incompatible ABI. Scope more than doubled, and a long
  rewrite went unmerged.
- **Failure:** a PRD locked that an errors tab writes issue state through a log vendor's API and
  keys on a `has_errors` column. The premise gate found that the API needs interactive OAuth for
  writes and that the column does not exist, before any code.

## 2. Walking skeleton & boundary-testing spike ACs (Step 2)

- **Good:** the single premise that could not be observed before the PRD (do partner CDN images
  render inside two host iframes under the declared CSP?) became Deliverable #1, blocking the
  downstream slices. It passed on day one.
- **Good:** a day-one go/no-go gate stood up the local database → change-capture → pub/sub emulator
  plane and caught a copy-phase transition gap on day one.
- **Failure:** a spike tested only backend REST pregeneration of wallets and reported PASS. It
  never tested a user claiming the wallet from a browser. Three weeks later a live end-to-end
  run showed email login creating a second user, and the pregenerate-and-claim design was deleted.
- **Failure:** a spike's AC hardcoded a client capability flag that is always false under the
  stateless transport the PRD chose.

## 3. Derive, don't restate; deletions; rungs (Step 3)

- **Good:** a first draft proposed about thirty manual annotations. Same-day adversarial review
  before code adopted "derive, don't restate": the facts came from existing funnel and predicate
  calls, annotations fell below ten, and a lint rule rejected restating derived facts.
- **Good:** a 29-rule "ladder shift" table moved 14 lint rules into compile-time types and deleted
  the redundant rules in the same PR.
- **Good:** the PRD named the four fire-and-forget onboarding functions to delete in the same commit.
- **Failure:** an onboarding state machine had no code-enforced completion fact for the signing
  key, so production accounts reached "complete" with a wallet and no bound key.

## 4. Day-0 contracts & multi-consumer seams (Step 4)

- **Good:** deliverable #1 shipped typed RPC interfaces plus an in-memory fake. Five parallel agent
  lanes then built and merged dozens of PRs in a few days without integration drift.
- **Failure:** a PRD deferred the shared accounts and rate-limit control plane and embedded auth
  and billing inside one worker. Within a day of lock, an uncached fan-out exhausted a Durable
  Object free-tier quota, and over a third of its decisions were superseded a week later.
