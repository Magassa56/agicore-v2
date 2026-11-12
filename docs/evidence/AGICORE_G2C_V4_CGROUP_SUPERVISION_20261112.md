# G2C V4: inherited evidence and cgroup supervision

The existing V3 1,000-observation report and its negative tests are retained
unchanged. They were produced under the V3 source closure at commit
`9e6eadcd81c2aec152872aa7783b5374e9731568`; they are not V4 receipts.
V4 authenticates the predecessor contract, report, negative report, and
archive by separately committed SHA-256 values, and checks the previously
registered fixtures, codec, tiers, and caps have not changed. It does not
rerun the six prior replays or claim a V4 tier-1,000 execution.

The V3 supervisor deliberately rejects nested cgroups. On the observed public
Linux runner the process was in `/system.slice/hosted-compute-agent.service`,
with 15,791,742,976 bytes of `MemAvailable` and 94,208,696,320 bytes free on
disk. The two visible non-root groups had `memory.max=max` and
`memory.high=max`. The kernel does not expose `memory.max` at the real cgroup
root. The V3 refusal and the raw measurements are preserved in
`AGICORE_G2C_5000_HOST_PREFLIGHT_GITHUB_7B93_20261112.json`.

V4 retains the V3 guard for V3 calls and introduces a separate check for the
initial cgroup-v2 namespace with the complete root mounted. It checks the
current process membership, every ancestor's hard and high memory limits and
CPU quota, root memory-controller availability, and free host resources. Any
unreadable, incomplete, or ambiguous hierarchy fails closed. Process-group
termination, inherited hard limits, per-process `prlimit`, and the original
resource budgets remain required.

The free-disk and memory readings are snapshots, and disk checks remain sampled
plus final rather than a real-time filesystem quota. The 5,000 replay requires
a separate successful preflight on its actual runner. No real DEVELOPMENT/OOS
data, 89,841-observation replay, broker, or real order is authorized.

The first replay workflow registration at commit `4f932f134c406c21aef35f4bde0b66d7160c2702`
was rejected before job creation because `runner.temp` was used in a job-level
environment expression. GitHub reported the error at line 30 in
https://github.com/Magassa56/agicore-v2/actions/runs/43131410993. No replay was
run by that invalid workflow. The following commit uses a fixed temporary path
on the fresh hosted runner and retains all preflight and process controls.

## First bounded 5,000 attempt

Commit `0ff5ed81e04a1ad95e960a26fcdcb691ebc042a2` ran
https://github.com/Magassa56/agicore-v2/actions/runs/43131684773 after the
same-host V4 preflight succeeded. No 1,000 replay was repeated. The 5,000
result was `BLOCKED`; the exact canonical tier report is retained as
`AGICORE_G2C_5000_TIER_REPORT_0FF5_20261112.json` with SHA-256
`9e36e021b23c9b9c9b92d330d1ab642727a5d349168b475a2752384412e2f4bc`.

- `constant-5000`: two independent producers and verifiers succeeded and the
  reference comparison passed. This case contained zero positions. The parity
  worker used 65.520 seconds CPU and 65.586 seconds wall time.
- `dense-5000`: the first producer succeeded in 24.115 seconds CPU and
  25.167 seconds wall time, with 365,228,032 bytes peak RSS and 79,732,736
  bytes physical output. The first verifier was terminated at the precommitted
  150-second CPU cap after 150.016 seconds CPU and 150.121 seconds wall time,
  with 508,723,200 bytes peak RSS. No dense verifier PASS, second production,
  dense parity, or overall 5,000 PASS was obtained.
- Initial execution-host headroom was 15,777,570,816 bytes effective available
  memory and 94,185,230,336 bytes free disk. Cgroup ancestors had unlimited
  `memory.max`, `memory.high`, and CPU quotas. The cap was not increased.

The attempt's archive step failed independently with `OSError: [Errno 27]
File too large` at its 32 MiB per-file limit. The reports were already emitted
to the GitHub job log and are retained here, but the full produced bundles
were not exported and cannot be reconstructed from the retained report alone.
There were no GitHub workflow artifacts. The archive procedure has since
been changed to bound its input selection and label omitted objects; this
does not recover the expired runner's bundles and does not rerun the replay.

The full regression and restricted portable jobs on the attempt commit both
passed: https://github.com/Magassa56/agicore-v2/actions/runs/43131684578.
The original PR #332 run on `c0842dc9bcd485de21fa20fb25640ea9407e9957`
remained queued with no jobs; GitHub provided no confirmed cause.
