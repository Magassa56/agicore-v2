# V2 synthetic storage proof — blocked

Status: `BLOCKED_STORAGE_CONTRACT_EQUIVALENCE`. Date: 2026-10-17T11:11:45.284486Z.

The first precommitted worker (`native-impulse_profit_LONG-1`) failed in the new
storage parser before a bundle manifest, summary or completion seal existed.
`_Parser.value` recognizes the keys `numerator` and `denominator` globally,
so it incorrectly treats the frozen schema's
`/result_schema/$defs/rational/properties` object as a rational value.
The offending values are schema descriptions, not integers.

The frozen runner produced and validated one 57-observation invented native
result. Its 75242 bytes and both partial shard objects are retained.
No exact roundtrip or independent audit completed. The supervisor stopped
after one failed worker; 149 workers remain unrun, including all 25 tamper cases.
No failure was removed, no codec or scenario was changed, and no retry occurred.

The fixture inventory was frozen before testing: 55 native fixtures and seven
codec fixtures, each planned twice in fresh processes. Six statistics vectors
and nine screening boundary cases were also predeclared; their worker was not run.
All proof source bytes remain exactly those in the pre-test source registration.

## Evidence

- Canonical proof JSON SHA-256: `0dc936418324850ffdc7817d9620d090b7049dd89189acf7d1f39fa1674a3285`.
- Fixture registration SHA-256: `60038227f5b57bf777149fad00e37ce764fc77169c5d26443aeeda664b98a714`.
- Source registration SHA-256: `cb8650fa6997f021fc678b5cd28814472c4145b075572b7b06fae8876aa8d32c`.
- Producer SHA-256: `3f0dad5ee903e56596416ee08db8718ab4be2a20dc9cb541ef4d2cd18c853e2d`.
- Verifier SHA-256: `ea5bc03772fd69124ffffe188c8d9544eed03b404c144b6c3ece044132a21f6e`.
- Complete source closure SHA-256: `8a188999dfeee33ea71a21327360f1d17962ab7b4083b690b08beef72233dc5c`.
- Verifier source closure SHA-256: `90d5b6866117ad03777835a4b510f2c5eca1d2ae99d7df8ce44b97d0a5417783`.
- Codec profile SHA-256: `9635d59d40eb747225a4c89c82302b0cbd87f38e337e3b6296039c70f139ce30`.
- Failed artifact archive: `EMA_PULLBACK_V2_STORAGE_PROOF_FAILED_20261017_V1.zip`, SHA-256 `34c1f0883a73f1acf857f6c650627de3c2aaf29c1b496aeb76002d0d59eab318`.
- Durable artifact ID: `libfile_b019531d54008191afd9b01465420123`, version 0.
- Independent retrieval matched the archive hash; every archived file hash matched.

Partial-attempt peak process-tree memory was 119156736 bytes
(conservative worker-peak plus supervisor-peak). The retained proof tree occupies
167936 physical bytes, including logs and directory metadata.
The archive and independently retrieved copy are additional preserved storage;
the final preservation checkpoint inventories them separately. No complete
bundle compression ratio or successful runtime is claimed.

## Unchanged constraints

Memory cap: 4,294,967,296 bytes. Storage cap: 8,589,934,592 bytes.
`PHYSICAL_CAP_EXCEPTION = PRECOMMITTED_NOT_ACTIVE`.
`RESOURCE_FEASIBILITY = NOT_PROVEN`.
The original claim remains unchanged; original invocations 1, recovery invocations 0.
No recovery claim, recovery run registration, real RAW access, real replay,
real performance result, OOS access or broker operation occurred.
Frozen strategy components, thresholds, lineage and the earlier WIP are unchanged.

Focused regression tests, repository CI and publication were not started after
the mandatory proof failure. No commit, push, PR or merge was performed.

Next: `AGICOREMANAGER_DECISION_ON_STORAGE_PARSER_FAILURE_REQUIRED`.
No repair or rerun is authorized by this blocked proof.
