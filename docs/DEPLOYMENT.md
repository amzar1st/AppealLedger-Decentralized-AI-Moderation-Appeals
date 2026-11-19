# Deploy and run in Studio

Use the public-content synthetic example in `examples/partnership.json`.

1. Open https://studio.genlayer.com and use its built-in account. Get test GEN through Studio's faucet if the deployment requires it. Never import a real-money wallet for this demo.
2. Import `contracts/appeal_ledger.py` using **Add From File**. The first two lines pin the GenVM runner and Python SDK; preserve them.
3. Open **Run and Debug** and choose **Normal (Full Consensus)**. Constructor: `appeal_window_seconds = 604800`, `review_window_seconds = 86400`.
4. Deploy. Wait for successful network execution; retain the contract address and transaction hash. `get_config` must return the expected windows and administrator.
5. Call `register_policy` as the deployer with the example's rule ID, rules and policy reference. Save the returned policy ID (normally `1`).
6. Call `register_decision` as deployer, passing the returned policy ID and the built-in address as author for a one-account demo. The `author` parameter is a hex **string** (`0x` plus 40 hex characters), validated and normalized by the contract. Copy the original text and SHA-256 exactly from the fixture. Save the returned case ID.
7. From the registered author account call `submit_appeal` with the example arguments and evidence.
8. Call `review_appeal(case_id)`. Wait for consensus. A failed or disputed transaction does not create a review. You may retry before the review deadline; never switch to leader-only mode to manufacture validation.
9. Call `get_case`. Check `status == REVIEWED`, the assessment, rule applicability and quotations. The example is expected to produce OVERTURN, but live model behavior must be observed, not assumed.
10. Call `finalize_appeal(case_id)`, wait for network finality, then `get_case` again. Check `status == FINALIZED`, verdict, finalization reason, exact hashes and four audit entries.

## Other outcomes

- UPHOLD: use a new case containing a direct sales advertisement that the policy explicitly forbids.
- INCONCLUSIVE: use a new case where the supplied original text lacks context required by the rule.
- Timeout: deploy a separate test instance with `60, 60`, appeal, allow the review window to elapse, then finalize without a review. This records `REVIEW_TIMEOUT`.

The contract can serve many cases and append many policy versions, while keeping one appeal per decision. Use a separate deployment per community. There is no upgrade or administrator replacement mechanism in this MVP.

## Exact content hash

```bash
python -c 'import hashlib; print(hashlib.sha256("EXACT ORIGINAL TEXT".encode("utf-8")).hexdigest())'
```

Avoid adding a trailing newline or altering Unicode whitespace when copying text.
