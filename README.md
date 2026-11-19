# AppealLedger — Decentralized AI Moderation Appeals

A standalone GenLayer Intelligent Contract for appeals against **public-content** moderation. It locks the exact policy version and original content, independently re-evaluates an appeal through GenLayer validators, and records `UPHOLD`, `OVERTURN`, or `INCONCLUSIVE` in an append-only case history.

## Quick start

1. Import `contracts/appeal_ledger.py` into [GenLayer Studio](https://studio.genlayer.com).
2. Use a Studio built-in account; no external wallet integration is required for this MVP.
3. Keep **Normal (Full Consensus)** enabled. Deploy with constructor inputs `604800` (7-day appeal window) and `86400` (1-day review window).
4. Follow [the sample case](examples/partnership.json) and [deployment walkthrough](docs/DEPLOYMENT.md).

```bash
python -m unittest discover -s tests -v
```

The tests use only Python's standard library. They test contract logic through a host double; they do not claim to emulate GenVM, network consensus, or live LLM accuracy.

## API

| Method | Caller | Behavior |
| --- | --- | --- |
| `register_policy(rule_id, rules, public_reference)` | Deployer | Append a new policy version; returns version ID |
| `register_decision(policy_version, author, content, content_hash, original_reason, public_reference)` | Deployer | Bind exact public text, SHA-256 and policy version; returns case ID |
| `submit_appeal(case_id, arguments, public_evidence)` | Registered author | Submit once, before the inclusive appeal deadline |
| `review_appeal(case_id)` | Anyone | Request independent validator review before the inclusive review deadline |
| `finalize_appeal(case_id)` | Anyone | Finalize agreed review, or record timeout as INCONCLUSIVE after deadline |
| `get_case(case_id)` | Anyone | JSON containing evidence, verdict, status and audit chain |
| `get_policy(policy_version)` | Anyone | JSON containing the immutable rules and policy hash |
| `get_config()` | Anyone | Administrator, time windows and counters |

All IDs are decimal strings. All timestamps are transaction-pinned UTC Unix seconds. Hashes are lowercase SHA-256 hex of the **exact UTF-8 text**, with no prefix or normalization. View responses are JSON strings.

## Consensus with substantive validation

The leader asks the LLM to classify rule applicability, violation and evidence sufficiency and provide exact policy/content quotations. Each validator **executes its own analysis without the leader answer in the prompt**, validates the leader's schema and quotations, recomputes its verdict, and requires exact agreement on those classifications and the derived verdict. Explanation wording may differ. This uses `gl.vm.run_nondet_unsafe`, with errors failing closed rather than accepting an unchecked result.

| Evidence | Rule applicable | Violation | Outcome |
| --- | --- | --- | --- |
| Insufficient | Any | Any | INCONCLUSIVE |
| Sufficient | Uncertain | Any | INCONCLUSIVE |
| Sufficient | No | Any | OVERTURN |
| Sufficient | Yes | Uncertain | INCONCLUSIVE |
| Sufficient | Yes | Yes | UPHOLD |
| Sufficient | Yes | No | OVERTURN |

A network disagreement is **not** an agreed INCONCLUSIVE decision. A failed review leaves the case pending; anyone can retry before its deadline. After that, anyone can finalize it as `INCONCLUSIVE` with `REVIEW_TIMEOUT`. This is separate from GenLayer's own transaction acceptance, appeal and finality lifecycle. Forum integrations should wait for network finality before honoring a case result.

## State and trust boundaries

`REGISTERED → APPEALED → REVIEWED → FINALIZED`, or `APPEALED → FINALIZED` after a review timeout. There are no edits, deletes, admin verdict overrides, reopened appeals or mutable policy records. New rule versions never change existing cases. Each case event binds a state hash and the previous event hash.

The deployer is the single community administrator in this MVP. It is trusted to register the real public policy, original post, reason and author address. Hashes prove internal integrity, **not** that a forum actually published those statements. A dishonest administrator can misregister facts; a production adapter needs authenticated source ingestion and author binding. An author cannot appeal from another address.

Only public content is supported. All evidence and arguments are permanently public. Do not submit private messages, credentials, sensitive personal data, or raw forum exports. References are audit pointers only: this contract never fetches them. The LLM sees a bounded, fixed snapshot. Prompt instructions treat user evidence as untrusted data, but prompt injection and correlated model errors remain possible. Exact quotations check grounding, not the truth of every conclusion.

Review/finalization are permissionless to prevent administrator censorship. There is no bond, fee market, transfer, automatic restoration, external forum adapter, or human escalation integration. A real forum must explicitly opt into the verdict and independently enforce it. Policies cannot be backdated: this MVP registers moderation decisions at transaction time and locks an already-registered version, rather than proving the historical policy effective at an external event.

## Project files

- `contracts/appeal_ledger.py`: single-file deployable contract with pinned GenVM/SDK runner.
- `tests/test_contract.py`: deterministic security, lifecycle and independent-validation tests.
- `examples/partnership.json`: synthetic public example and exact content hash.
- `docs/DEPLOYMENT.md`: Studio setup, methods and verification.
- `docs/VALIDATION.md`: validation scope and deployment evidence.

## References

- [GenLayer custom nondeterministic validation](https://docs.genlayer.com/developers/intelligent-contracts/features/non-determinism)
- [Transaction context and deterministic time](https://docs.genlayer.com/developers/intelligent-contracts/features/transaction-context)
- [GenLayer Studio](https://docs.genlayer.com/developers/intelligent-contracts/tools/genlayer-studio)

MIT licensed. Experimental developer MVP; no claim of production readiness or guaranteed moderation accuracy.
