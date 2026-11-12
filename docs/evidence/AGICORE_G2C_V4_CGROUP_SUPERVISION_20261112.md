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
