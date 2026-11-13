# Test-Diff Review Heuristics

Mechanical detectors over a **test diff** — run them on yourself before opening a PR, and implement them as CI annotations (they are the per-PR form of the audit detectors that find corpus-wide test debt).

Every detector is a *review trigger*, not an auto-reject: a hit means "justify or fix", where justification is one docstring/PR sentence.

## The detectors

| # | Detector | Rule (on each new/modified test function) | Hit means |
|---|---|---|---|
| 1 | **no-oracle** | No `assert`, `pytest.raises`/`warns`, or mock assertion in body | Vacuous — delete, or state the does-not-raise contract in the docstring and assert something real |
| 2 | **missing value sentence** | Docstring absent or doesn't state a failure mode | The value gate wasn't run — add the sentence or drop the test |
| 3 | **interaction-only** | Only oracle is a mock call assertion | Choreography — assert returned/persisted state unless the call is the contract (say which) |
| 4 | **mock-heavy** | ≥5 `Mock`/`patch`/`monkeypatch` constructions | Topology rebuild — introduce a fake at the boundary (`mocking-and-seams.md`) |
| 5 | **config mirror** | ≤10 lines, control-flow-free, asserts equality against a literal on a config/default/enum/model attribute | Mirror — delete or fold into the surface's one parameterised contract table |
| 6 | **private-attribute reach** | Asserts on `obj._name` of a non-test object | No consumer, no contract — delete |
| 7 | **member-count pin** | `len(SomeEnum) == N` or equivalent | Breaks on valid additions — pin wire values in a contract table instead |
| 8 | **duplicate body** | Normalised AST body identical to an existing test | Consolidate, or document the distinct boundary in both docstrings |
| 9 | **tautology** | Expected value computed from the same inputs by the same operation as the code under test | Passes by construction — use an independent literal |
| 10 | **source-shape test** | Body reads/parses source via `ast`/`inspect`/`read_text` | Architecture rule in the wrong lane — move to a named ast-grep/lint rule with fixtures |

## Self-review pass (run now, no tooling)

```bash
# Your test diff
git diff main...HEAD -- tests/

# 5/6/7: mirrors and private reaches in the diff
git diff main...HEAD -- tests/ | grep -nE '^\+.*assert.*\b_[a-z_]+\b|^\+.*len\([A-Z][A-Za-z]*\)\s*==\s*[0-9]'

# 4: mock density per added test (eyeball anything dense)
git diff main...HEAD -- tests/ | grep -cE '^\+.*(Mock\(|patch\(|monkeypatch\.)'

# 1: added tests with no visible assertion — list added defs, then check each
git diff main...HEAD -- tests/ | grep -nE '^\+\s*(async )?def test_'
```

Then read each added test once asking only: *what failure mode reddens this, and is the oracle real?*

## CI gate spec (for implementers)

- **Where:** a PR-diff job in CI, annotation-mode (`warn`), promotable to blocking per-detector once the false-positive rate is known. Detectors 1, 6, 7 are safe to block from day one.
- **How:** one AST script over `git diff --name-only` test files, reusing the audit's census detector semantics; emit GitHub annotations at the offending line with the detector name and the one-line fix.
- **Escape hatch:** an explicit justification marker in the docstring (e.g. `contract:` followed by the owner/consumer) suppresses 3, 5, 7, 8 — making the justification durable and greppable, which is the point.
- **Non-goals:** never run corpus-wide in the PR gate (that's the audit's job, quarterly); never count coverage; never require a test to exist — this gate only inspects tests the diff *adds*.

## Sibling gate (verification-before-completion)

"N tests added, all green" is not completion evidence. Completion evidence for test work is: each new test's docstring completes the value-gate sentence + red-then-green observed in session output + a clean detector pass over the diff.
