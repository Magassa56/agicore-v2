# Portable verifier: independent synthetic fixture V9

This source-checkout integration verifies portable archive integrity. It does not
replay a strategy, validate trading results, establish original runtime equivalence,
or establish feasibility for 89,841 observations.

## Two explicit modes

**REPOSITORY_SELF_CONTAINED_NONWORKER_TESTS** uses only repository source and
`tests/fixtures/ema_pullback_v2_portable_synthetic_v1.zip`. The new S01, S02, S03 and
SN01?SN30 protocol cases are synthetic. S03 writes a synthetic supplemental receipt;
it is not historical P03. No historical archive or evidence directory is consulted.
The unit tests also cover 19 inventory regressions, eight raw path probes, runtime
metadata, inconsistent origins, resources, explicit CLI modes and output collisions.

**EXTERNAL_HISTORICAL_EVIDENCE_VERIFICATION** is a separately authorized operator
operation. Supply `--historical-archive PATH` explicitly. The frozen V2 contract
checks the exact historical SHA256
`559ab5ba4c0f65b2f899b3c19c6031af71556d4571500da5ad0f10392423a07d`.
Absent or wrong input fails. There is no synthetic fallback. The original archive
is not included or authorized for publication. Ordinary tests only confirm this
mode rejects new synthetic bytes and a missing path; they do not execute historical P03.

Historical V7 remains bound to verifier
`b5c4cc66a2702488913e1e28ed664135b2f7b935819261c8325d9a6dc788368f`, plan
`d0ece951ddd0785055fe2d1c005bbfb05dc53aa5509b0144c2413bf9e8c17edd`, and checkpoint
`26fcf073948670b99af4295b019b8a0f9c0379a0a67dc98db88c1146eddc2fa6`.
V8 admission checkpoint is
`d0192f0238ef78b5d463187fa7d1086f984219127b35ae14abf305c60d8c5d05`.
Neither historical plans nor receipts are rewritten or aggregated with V9.
The historical P01 correction contract is retained byte-for-byte. Its old machine
paths remain historical documentary fields; ordinary tests never resolve them.

## New fixture commitment and construction

Schema: `agicore:portable-synthetic-fixture:v1`.
Fixture bytes: 14690. Fixture SHA256: `a6f1a6c6c68cf7ed5be3c686e438d85cbd8753762fd9c7e2bb1a01d46c583dec`.
Expected complete native bytes: 784. Native SHA256: `fd03c5fd04124072c155ef5a4fcf6af64037a78f07012129ab122c7f8ff7d983`.

AGIcoreManager explicitly authorized construction and repository inclusion of this
new independent synthetic fixture in V9. All contents are invented protocol test
material defined in `synthetic_native()` and `build_synthetic_fixture()` in the
portable unit test module. No input or receipt is copied from a historical archive.
It contains no controller source, bytecode, failed-run trace, runtime archive,
credential, market dataset or private source. Receipt/audit PASS fields describe
only the invented protocol structures; no actual producer or scientific audit ran.
Legacy on-wire schema/field names are retained because verifier semantics are frozen.

Construction uses only Python standard-library operations and a digit-by-digit
JSON integer oracle separate from the verifier serializer. Counts are explicitly
specified. SHA256 commitments, source/run bindings, expected native bytes and trust
are independently declared outside the archive. No trust document is loaded from
inside the archive. `FIXTURE_SHA256` and `EXPECTED_NATIVE_SHA256` are pinned constants.

All ZIP names are sorted ASCII POSIX names; entries are ZIP_STORED, fixed at
2000-01-01 00:00:00, create_system=3, regular-file mode 0444. No extraction occurs.
The native shard is a frozen literal RAW_DEFLATE stream, generated once from the
invented native bytes. The witness shard is IDENTITY. Regeneration copies those
literal bytes and does not recompress with an arbitrary host library.
`build_synthetic_fixture()` returns the exact full archive bytes and external trust;
it never calls the verifier, original producer, proof controller or strategy runner.

Construction runtime: CPython 3.12.10, zlib compile/runtime 1.3.1.
Construction Python executable SHA256: `4d6f5f81a4bca11191c4c7c6b43632694d0a4ce74e068619d8fdc161d469859a`.
The fixture codec declaration is new synthetic metadata; it replaces no registered
historical codec profile. Runtime identities of later consumers are recorded separately.

Regeneration (construction only, preserving the original file):

```python
from pathlib import Path
from tests.unit import test_ema_pullback_v2_portable_verifier_v2 as t
raw, trust = t.build_synthetic_fixture()
assert t.digest(raw) == t.FIXTURE_SHA256
assert raw == t.SYNTHETIC_PATH.read_bytes()
# Write raw only to a new operator-selected path if a copy is needed.
```

Exact expected native UTF-8 bytes are the following JSON plus one final LF:

```json
{"closed_trade_records":[],"dataset_id":"portable-invented-v1","dataset_lineage_manifest_sha256":"5276d8d4bd62c7d4d565f65a96b24454ea32da635de608bb162c2fc1329e786d","dataset_role":"SYNTHETIC_TEST_ONLY","formalization_version":1,"marked_equity_samples":[{"ordinal":0,"value":7}],"metrics":{"average_trade_usd":{"denominator":3,"numerator":1}},"output_sha256":"25febef67cff8cea6630190a818bbe9e51c86e6d40bb0e2a18e6bd2308a29b6e","run_id_sha256":"3797119dcd45696b93c5637252bc05a9f323eca8ce1187e500a9b241a519e337","run_identity":{"declaration":"INVENTED_PROTOCOL_TEST_NO_TRADING_EXECUTION","schema":"agicore:portable-synthetic-fixture:v1","source_sha256":"68f251bbf7e7ae75a0bab32e0f930e4829ed6475f4f68acd6b8d50e20dbbca2c"},"synthetic_fixture_schema":"agicore:portable-synthetic-fixture:v1"}
```

## Run only the inspected tests

From the repository root, with test dependencies already available:

```text
python -B -m pytest -c pyproject.toml --noconftest -o addopts= -p no:cacheprovider -p no:junitxml -q -rA -x tests/unit/test_ema_pullback_v2_portable_verifier_v2.py tests/integration/test_ema_pullback_v2_portable_verifier_v2.py
```

Set `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and `PYTHONDONTWRITEBYTECODE=1` in the shell.
For isolated outputs, set `AGICORE_PORTABLE_EVIDENCE` to an operator-selected scratch
parent. Every case creates a unique child directory. Configure pytest `--basetemp`
with a new scratch path and TEMP/TMP/TMPDIR outside the checkout when required.
`--noconftest` avoids the existing root test conftest, which redirects temporary
files inside the checkout. No existing conftest fixture is needed by these tests.
`-c pyproject.toml` avoids unrelated pytest.ini options; no tests are skipped.
No JUnit report is requested: pytest's JUnit emitter queries hostname. The V9 run
records exact collection, terminal per-node outcomes, and per-case JSON receipts.
A fresh plan outside Git pins the exact 79-node inventory before execution.
Stop at the first failure. Never automatically repair and rerun under that plan.

The CLI generic mode requires both `--archive PATH --trust PATH`; save the trust
JSON below into a separate operator-selected file, then run:

```text
python -B tools/ema_pullback_v2_portable_verifier_v2.py --archive tests/fixtures/ema_pullback_v2_portable_synthetic_v1.zip --trust TRUST_FILE --output-root NEW_RECEIPT_PARENT
```

The CLI creates a unique receipt child directory, opens its fixed output filename
exclusively, and never maps ZIP member names to filesystem output paths. Original
inputs are read-only operations. No archive is selected implicitly.

## Runtime identity and limits

Metadata uses sys.version_info, sys.implementation, sys.platform, interpreter bytes,
zlib versions and the actual module spec. No platform.node/uname/platform or socket
hostname call is used. Built-ins require genuine loaded BuiltinImporter provenance,
no separate file, and bind to the interpreter SHA256 by the registered convention.
File-backed extensions require consistent loader/spec/module paths to an actual
regular extension file; its bytes are hashed. Unsupported/inconsistent origins fail
closed. These facts do not claim original runtime equivalence or historical profile replacement.

Optional Windows measurements use GetProcessMemoryInfo (peak working set and peak
commit). Linux uses getrusage(RUSAGE_SELF).ru_maxrss in KiB, converted to bytes;
commit is NOT_MEASURED. Unsupported/unavailable values are NOT_MEASURED with null
metrics and a reason. Measurements never claim enforcement. Linux code inspection
and a synthetic file-backed spec test do not establish execution on Linux.

Required V9 execution caps: aggregate/process memory 512 MiB, total collection/test
wall time 600 seconds, new evidence 64 MiB. A one-use external resource wrapper
applies Windows Job Object commit limits and monotonic/output watchdogs around the
ordinary pytest command. This wrapper contains no fixture or case implementation
and is not a repository/test dependency. If enforcement fails, no test may start.
Archive validation retains its original byte/depth/integer/member/decoder bounds.
No clean-checkout reproduction or Linux PASS is claimed by this document.

## CI safety proposal ? separate authorization required

No workflow is modified in V9. `.github/workflows/agicore-ci.yml:unit-tests` and
`main-ci-cd.yml:test` currently run `python -m pytest -q`. The existing storage tests
call native_case, byte_case and tamper_case; native_case invokes synthetic strategy
replay and the storage producer. Other development replay tests also run invented
strategy processing. They are outside this phase, even without worker subprocesses.

Proposed portable job: the two-file selection above, explicit collection inventory,
Windows and Linux executions on identical frozen sources, bounded resources, exact
negative layers, and published receipts/artifacts. Report excluded storage/replay
node groups and reasons. Preserve broader coverage in separately authorized jobs
with explicit worker/replay permission, bounded resources and pinned inputs. Never
claim the portable selection equals the full suite or silently delete broader tests.
Use verification jobs independent of the manual Cloud Run deployment workflow;
deployment remains default-off and requires separate explicit authorization.

## V9 source transition

The archive-to-seal validation definitions and `verify_archive(raw, trust)` remain
unchanged from V7. Changes are limited to metadata/resource/CLI plumbing and the
synthetic test fixture/harness. Original 35/35 and 9/9 scientific source closures
remain unchanged. The external V9 plan pins this document's own SHA256 and all
source, fixture, runtime and execution identities before collection/testing.

| Source | SHA256 |
|---|---|
| `tools/ema_pullback_v2_portable_verifier_v2.py` | `7b3ac923e731603e17171c0ec00e93759994dfeee1cfd31b574e239078fd083c` |
| `tests/unit/test_ema_pullback_v2_portable_verifier_v2.py` | `a38089514312b2908045cdbc6f7866fd76b99bed0cf8ab2cec900ed0cfbe6db4` |
| `tests/integration/test_ema_pullback_v2_portable_verifier_v2.py` | `c73795f32cd9d3deadce4bfb09a5803c65b0b6608cfc69a7ca8ed044d4c78aef` |
| `.gitattributes` | `6afe84470a13b4d6d065950d32c209af5b9d400037bdc3bfab003459d73521ad` |
| `docs/evidence/EMA_PULLBACK_V2_PORTABLE_VERIFIER_P01_CORRECTION_PLAN_V2.json` | `4b524c51f36de3daffcb503b93ae8e5b8b7887e6c3bb81c6e586181923509bea` |

The old verifier identity is historical evidence, not the identity of this new
CLI/runtime implementation. V9 execution results must be read only from its new
checkpoint; historical V7 remains a separate 33/33 result.

<!-- synthetic-trust-v1 -->
```json
{
  "archive_sha256": "a6f1a6c6c68cf7ed5be3c686e438d85cbd8753762fd9c7e2bb1a01d46c583dec",
  "bindings": {
    "complete_source_closure_sha256": "2da4c0d1185f6f682aa8069dc2ef4716dbb6f12cf8c33c42480ff3042052a240",
    "dataset_lineage_manifest_sha256": "5276d8d4bd62c7d4d565f65a96b24454ea32da635de608bb162c2fc1329e786d",
    "dataset_raw_sha256": "68f251bbf7e7ae75a0bab32e0f930e4829ed6475f4f68acd6b8d50e20dbbca2c",
    "run_id_sha256": "3797119dcd45696b93c5637252bc05a9f323eca8ce1187e500a9b241a519e337",
    "run_identity": {
      "declaration": "INVENTED_PROTOCOL_TEST_NO_TRADING_EXECUTION",
      "schema": "agicore:portable-synthetic-fixture:v1",
      "source_sha256": "68f251bbf7e7ae75a0bab32e0f930e4829ed6475f4f68acd6b8d50e20dbbca2c"
    },
    "storage_addendum_sha256": "5d1f84fad2010d5884bd6819add27bef2a26368d1b7130cbc316d78cdb9138db",
    "synthetic_fixture_schema": "agicore:portable-synthetic-fixture:v1",
    "verifier_source_closure_sha256": "8eb2ddfdcd30f3d1a00d825c72b2fe8c300cc64a5c29f85ddd70dd05051771a3"
  },
  "bundle": "bundle/",
  "embedded_output_sha256": "25febef67cff8cea6630190a818bbe9e51c86e6d40bb0e2a18e6bd2308a29b6e",
  "file_inventory_sha256": "e0ecb047e5a869bfad26d41e9596d6afe4b4a39e20f3aaae384ea6224d34ebb2",
  "historical_audit": {
    "native_output_sha256": "25febef67cff8cea6630190a818bbe9e51c86e6d40bb0e2a18e6bd2308a29b6e",
    "observation_count": 1,
    "status": "PASS",
    "strategy_recomputed": false,
    "synthetic_protocol_structure_only": true
  },
  "independent_sha256": "960033a5098bddab8d3a7f1b3c76226a0eaa84fd1f6ea8304adaa2c55d6ed968",
  "manifest_sha256": "87a30a4d1b23141f3aebc26cce545acdb1dcb2cc83054a23b2f0ac1553f5066a",
  "members": [
    {
      "compressed_size": 1585,
      "compression": 0,
      "crc32": 2949610200,
      "external_attr": 2166620160,
      "name": "portable-synthetic-v1/FILE_INVENTORY.json",
      "sha256": "e0ecb047e5a869bfad26d41e9596d6afe4b4a39e20f3aaae384ea6224d34ebb2",
      "size": 1585
    },
    {
      "compressed_size": 2603,
      "compression": 0,
      "crc32": 1994293872,
      "external_attr": 2166620160,
      "name": "portable-synthetic-v1/bundle/bundle-manifest.json",
      "sha256": "87a30a4d1b23141f3aebc26cce545acdb1dcb2cc83054a23b2f0ac1553f5066a",
      "size": 2603
    },
    {
      "compressed_size": 1835,
      "compression": 0,
      "crc32": 616296597,
      "external_attr": 2166620160,
      "name": "portable-synthetic-v1/bundle/completion-seal.json",
      "sha256": "60fb66691ed9ff5a37d19e2a4271d37079b241180b92da06031028f3145f3140",
      "size": 1835
    },
    {
      "compressed_size": 1296,
      "compression": 0,
      "crc32": 1876582159,
      "external_attr": 2166620160,
      "name": "portable-synthetic-v1/bundle/decision-summary.json",
      "sha256": "c380176489509ce3cff5a2e6f59470063c6780f0979888bff50ecebb6150bb38",
      "size": 1296
    },
    {
      "compressed_size": 1739,
      "compression": 0,
      "crc32": 3747481201,
      "external_attr": 2166620160,
      "name": "portable-synthetic-v1/bundle/independent-verification.json",
      "sha256": "960033a5098bddab8d3a7f1b3c76226a0eaa84fd1f6ea8304adaa2c55d6ed968",
      "size": 1739
    },
    {
      "compressed_size": 501,
      "compression": 0,
      "crc32": 1061450723,
      "external_attr": 2166620160,
      "name": "portable-synthetic-v1/bundle/objects/32/326fea740c6722337986ecba4d0a859798d51f70abc070c414e9863c9ca1449e.blob",
      "sha256": "326fea740c6722337986ecba4d0a859798d51f70abc070c414e9863c9ca1449e",
      "size": 501
    },
    {
      "compressed_size": 31,
      "compression": 0,
      "crc32": 3251078531,
      "external_attr": 2166620160,
      "name": "portable-synthetic-v1/bundle/objects/97/9779cb5268f90af090dad2a8bbef6173224e6411611fe28a27bcfaeba02b9962.blob",
      "sha256": "9779cb5268f90af090dad2a8bbef6173224e6411611fe28a27bcfaeba02b9962",
      "size": 31
    },
    {
      "compressed_size": 1438,
      "compression": 0,
      "crc32": 4064592310,
      "external_attr": 2166620160,
      "name": "portable-synthetic-v1/bundle/production-receipt.json",
      "sha256": "76abfe9541ba1edaa0b3c39b878ea619c2cc9b0613d68ccb689aa17fd63558e1",
      "size": 1438
    },
    {
      "compressed_size": 636,
      "compression": 0,
      "crc32": 717408919,
      "external_attr": 2166620160,
      "name": "portable-synthetic-v1/invented.receipt.json",
      "sha256": "7d46465ef60d4d7498de0248b20e2e750e1f738e6b372cd5284891d1d1125fef",
      "size": 636
    },
    {
      "compressed_size": 784,
      "compression": 0,
      "crc32": 356856125,
      "external_attr": 2166620160,
      "name": "portable-synthetic-v1/invented/reference-native.json",
      "sha256": "fd03c5fd04124072c155ef5a4fcf6af64037a78f07012129ab122c7f8ff7d983",
      "size": 784
    },
    {
      "compressed_size": 48,
      "compression": 0,
      "crc32": 3937536589,
      "external_attr": 2166620160,
      "name": "portable-synthetic-v1/invented/synthetic-source.Last.txt",
      "sha256": "68f251bbf7e7ae75a0bab32e0f930e4829ed6475f4f68acd6b8d50e20dbbca2c",
      "size": 48
    }
  ],
  "native_sha256": "fd03c5fd04124072c155ef5a4fcf6af64037a78f07012129ab122c7f8ff7d983",
  "production_sha256": "76abfe9541ba1edaa0b3c39b878ea619c2cc9b0613d68ccb689aa17fd63558e1",
  "profile": {
    "algorithm": "RAW_DEFLATE",
    "construction": "FROZEN_LITERAL_BYTES_NO_RUNTIME_RECOMPRESSION",
    "profile_id": "PORTABLE_SYNTHETIC_FROZEN_BYTES_V1",
    "window_bits": -15
  },
  "profile_sha256": "fdffa23d796fad7f04df135d2c62a1f969cb3ac5a7c3bada7f86f8da493cc1af",
  "reference_sha256": "fd03c5fd04124072c155ef5a4fcf6af64037a78f07012129ab122c7f8ff7d983",
  "root": "portable-synthetic-v1/",
  "seal_sha256": "60fb66691ed9ff5a37d19e2a4271d37079b241180b92da06031028f3145f3140",
  "summary_projection_fields": [
    "dataset_id",
    "dataset_role",
    "formalization_version",
    "metrics",
    "output_sha256",
    "run_identity",
    "run_id_sha256",
    "dataset_lineage_manifest_sha256",
    "synthetic_fixture_schema"
  ],
  "summary_sha256": "c380176489509ce3cff5a2e6f59470063c6780f0979888bff50ecebb6150bb38",
  "worker": "invented/"
}
```
