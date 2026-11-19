# Validation record

Checked 2026-11-19.

- 17 standard-library unit tests passed. Includes all verdict branches, permissions, exact hashes, immutable policy versions, one appeal per decision, inclusive deadline boundaries, timeout finalization, substantive validator disagreement, malformed model output, alternative explanation wording, and audit-chain integrity.
- Python source compilation passed.
- GenLayer Studio schema generation passed using GenVM v0.2.16 and the SDK runner pinned in the contract header.
- Hosted Studio deployment finalized in Normal (Full Consensus) mode using a built-in Studio account.
- Contract: `0x2504bB39788964ef156D608cDd1B45cAD1878699`
- Deployment transaction: `0xa8d03810f005ff2792ac7bad206865da982cb68b55565d029c75f01938ceff7a`
- Deployer: `0xd410A16A05022918E5F8FBC0f4aCBA41AD86F00C`
- `get_config()` returned windows `604800` and `86400` and the expected owner.
- Sample policy registration finalized: `0x6fff1eefdf0357e43bbf31985646a2fe831c37b197e2920746857e2a58a775aa`.

Live appeal lifecycle verification is recorded below when complete. Local host-double tests do not establish real validator participation, model accuracy, sandbox isolation or GenVM rollback behavior. Hosted Studio is a development network and may reset.
