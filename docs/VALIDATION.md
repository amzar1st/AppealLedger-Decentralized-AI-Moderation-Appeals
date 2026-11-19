# Validation record

Checked 2026-11-19 on hosted GenLayer Studionet. This is a development-network deployment, not mainnet.

## Automated checks

18 standard-library unit tests passed locally and in GitHub Actions. Python source compilation passed. Coverage includes all three verdicts, permissions, exact text hashes, immutable policy locking, one appeal per decision, inclusive deadline boundaries, timeout finalization, substantive validator disagreement, malformed model output, alternative reasoning wording, hex-address validation and audit-chain integrity.

The tests use a host double, not a GenVM emulator. Live Studio testing separately verified schema generation, storage behavior, address decoding, deployment and independent LLM review. During that check, Studio's Address-typed input was found to arrive as an integer; the released interface instead accepts a strict hex string and normalizes it through the SDK Address constructor. Earlier experimental deployments are superseded and must not be used.

## Released deployment

- Contract: `0x30015bfEE37c45D4D69b7Ad81207EAD2cbB0a18c`
- Explorer: https://explorer-studio.genlayer.com/address/0x30015bfEE37c45D4D69b7Ad81207EAD2cbB0a18c
- Deployer: `0xd410A16A05022918E5F8FBC0f4aCBA41AD86F00C` (built-in Studio account)
- Execution mode: Normal (Full Consensus); simulation mode disabled.
- Constructor windows: `604800` seconds for appeals, `86400` seconds for review.
- Runner: GenVM v0.2.16, SDK hash pinned in the source header.

| Step | Transaction hash |
| --- | --- |
| Deploy | `0x2dc538ddb0b09c7e133f8577c956c7b07198fcf64e5a96a8e02cc2f02f4f4f43` |
| Register policy 1 | `0xff793b7e2dd892b5f17e5c0bd169b9cc35b605ab225dfabe00dbab2006d6fa93` |
| Register case 1 | `0xf63031e2cbcb14bcd54a6d42a02658b70d13408f67a536c07b4050b6ae4ca68a` |
| Submit appeal | `0xfcbdc1570719f5c86e5fd0ef55ea76324f9d6271d6b60d38d073a8deb246e1a0` |
| Independent review | `0x340af95fcffe91773dc01a0b21907300108af67bed922c048959a0c368969343` |

The review transaction finalized with GenVM `SUCCESS` and consensus `Accepted`. The explorer reported five initial participants, three `agree` votes and two `idle` entries; the three completed validator receipts reported `SUCCESS` with matching state hashes. This record does not claim all five completed analysis.

The live assessment was applicability `YES`, violation `NO`, evidence `SUFFICIENT`, verdict **OVERTURN**. Its exact policy quote was the governance partnership exception. The explanation states that the post seeks a member vote rather than a product purchase and that naming a commercial partner alone does not establish advertising.

Local tests cover UPHOLD, INCONCLUSIVE, timeout handling, malicious or malformed responses and disagreements. These branches were not all exercised against live models. A successful synthetic case does not establish general moderation accuracy, prompt-injection resistance or production readiness. Studio state may reset.

## Finalized live case

Finalization transaction `0xe319b70222105331b6cdc22bfa5a922efadfc594d2cbb1e5361eae60378696a3` finalized successfully. A fresh `get_case("1")` read against **Finalized** state returned `status: FINALIZED`, `verdict: OVERTURN`, `finalization_reason: VALIDATOR_REVIEW` and four audit entries. The exported [live case](../examples/live_case.json) was independently checked for all event hashes, previous-hash links and the final state hash. [Explorer screenshot](deployment.jpg) records all six lifecycle transactions finalized with GenVM SUCCESS.
