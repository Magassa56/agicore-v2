# EMA_PULLBACK_V2 recovery storage parser targeted repair V1

Status: `PATCHED_FIRST_WORKER_PASS`.

Canonical evidence JSON SHA-256:
`f8ad80c3451f0db083eb86f032af839a243cff66e3ec05d3cc79a4cd72297422`.

## Scope

This checkpoint repairs only the confirmed parser ambiguity from the first failed
bounded synthetic storage worker. It does not complete the 150-worker proof, prove
89,841-bar resource feasibility, register a recovery run, or authorize any real replay.

The historical workspace remains unchanged. Its Git pointer is broken because it
targets an absent former workspace, but all required source, fixture, log and evidence
bytes were recovered and hashed before use. Work continued in a fresh checkout of
`6d01dd3826320270dab5ce75062170d77d22d3af` on
`feature/ema-pullback-v2-recovery-storage-parser-repair`.

## Root cause and repair

The original `_Parser.value` assigned rational semantics to every object whose keys
were exactly `numerator` and `denominator`. It therefore treated the JSON Schema node
`/result_schema/$defs/rational/properties` as a numeric rational.

The repair removes this key-name heuristic. The exact parser now validates a rational
only when an explicitly supplied applicable schema resolves to `#/$defs/rational`.
Schema declarations and ordinary homonymous objects remain ordinary JSON objects.
Actual rationals still require true integers (never booleans), a positive denominator,
and reduced exact form. No float, tolerance, schema edit, codec edit, chunking edit, or
strategy edit was introduced.

## Focused validation

- Parser assertions: **24 passed**, 0 failed in 0.55 seconds.
- Ruff check: **PASS**.
- Ruff format check: **PASS**.
- Python compilation: **PASS**.
- Historical first worker `impulse_profit_LONG`: **PASS** on 57 invented observations.
- Reference native SHA-256:
  `420cb64cfceab0ae4bf761ab3ac9ba8b8d08a1ef75eec837f66f954713ec2913`.
- Reconstructed native SHA-256: identical.
- Exact native bytes: **TRUE**.
- Independent verification: **PASS**.
- Completion seal SHA-256:
  `5485a2e8700ceddb853be5fb9d05260b4c26f045d24bf6d21b47a06a33a8ff7c`.

Two preliminary commands failed before importing `_worker` because the isolated clone
was not installed and then lacked the test site-packages on `PYTHONPATH`. Neither
created a case directory or executed the synthetic worker. The bounded worker was then
run once with the required import paths and completed successfully.

## Source transition

| Binding | Historical blocked source | Targeted repair source |
|---|---|---|
| Producer | `3f0dad5ee903e56596416ee08db8718ab4be2a20dc9cb541ef4d2cd18c853e2d` | `bbfc658310f27af6a03b34e8771205af84843b97315266098f21725ebfec03d3` |
| Verifier | `ea5bc03772fd69124ffffe188c8d9544eed03b404c144b6c3ece044132a21f6e` | `9e04e9da8eef04eddaa0c7db53bca6831570416955b5d2c518d6d26a991a1da8` |
| Complete closure | `8a188999dfeee33ea71a21327360f1d17962ab7b4083b690b08beef72233dc5c` | `7a730b86b51fd1c063cc7ea637763009d2bf303a9d1b4afa879e99116ec077ec` |

The historical failure traceback SHA-256 remains
`b8935867e5364e09ec28c7bd2abbbf929c6e9ff5ebb5eb90e16ffe9578301d8e`.
The original execution claim remains byte-identical with SHA-256
`d2eb78fb5a1b97e71fcc323b71da216449b35e4298729a26d6d052f4f26f00f4`.

The 38-file preservation inventory has SHA-256
`dfa37fcf85f1c66d511e27d2aae295261c3f52f7aa3d4c6242a2879354cc4df2`.
The independently re-read compact archive has SHA-256
`72b79c1a9b02c8ac7924fecc349a8b7764da69f38b7c7dcb8d0bf67dd07c5888`
and size 103,226 bytes. It excludes the original claim and all real/OOS data.

## Governance boundary

`FULL_SYNTHETIC_PROOF = NOT_COMPLETED` and
`RESOURCE_FEASIBILITY_89841 = NOT_PROVEN`. No real DEVELOPMENT data, recovery replay,
recovery claim, recovery run registration, performance metric, verdict, OOS data,
broker, or paper order was accessed or created.

Next gate:
`EMA_PULLBACK_V2_RECOVERY_STORAGE_SYNTHETIC_PROOF_CONTINUATION_REQUIRED`.
