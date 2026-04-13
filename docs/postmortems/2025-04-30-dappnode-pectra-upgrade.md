# Post-Mortem: DAppNode Package Readiness for Pectra Upgrade

**Date**: April 30, 2025
**Severity**: Moderate (validator participation impact, no consensus failure)
**Networks affected**: Gnosis Mainnet
**Summary**: DAppNode packages for Gnosis were not owned by the Gnosis core team going into the Pectra hard fork. This led to last-minute manual package updates, with some clients (Erigon, Geth) leaving DAppNode validators unable to follow the fork cleanly.

## Timeline

- **Mar 12, 2025** -- Core devs call flags DAppNode package ownership as unresolved: "DAppNode packages ownership: we should claim ownership of those."
- **Apr 9, 2025** -- [PR #74](https://github.com/gnosischain/specs/pull/74) merged, scheduling Pectra activation on Gnosis mainnet (epoch 1337856, Apr 30).
- **Apr 23, 2025** -- Core devs call one week before fork. DAppNode packages still listed as "To do / Manual updates today." Nethermind v1.31.8 released.
- **Apr 30, 2025** -- Pectra activates on Gnosis mainnet at epoch 1337856.

### Client release timeline (Pectra-compatible versions)

| Client | Version | Notes |
| --- | --- | --- |
| Nethermind | v1.31.8 | Released Apr 23 -- one week before fork |
| Erigon | v3.0.2 | Major version bump from v2; required full resync (~2 hours on DAppNode) |
| Geth | -- | Broken CI; no Pectra-compatible release available at fork time |
| Lighthouse | v7.0.0 | Ready |
| Teku | v25.4.1 | Ready |
| Nimbus | v25.4.0 | Ready |
| Lodestar | v1.29.0 | Ready |

## What Went Wrong

### 1. DAppNode package ownership was not established before the fork

Gnosis DAppNode packages were not owned or controlled by the Gnosis core team. Package updates could not be pushed directly and had to be coordinated externally or applied manually by node operators. As of the April 23 core devs call, packages were still being updated manually -- one week before fork activation.

### 2. Erigon v2 to v3 migration required a full resync

The Pectra-compatible Erigon release (v3.0.2) was a major version bump from v2. On DAppNode, this upgrade required a full resync taking approximately 2 hours. DAppNode validators running Erigon who updated close to the fork missed the activation window while their node resynced. This was flagged publicly: "Full resync required (~2 hours). May cause temporary hard fork participation gap."

### 3. Geth had no working Pectra-compatible release

Geth's CI was broken, and no Pectra-compatible build was available for DAppNode users at fork time. Any DAppNode validators running Geth had no upgrade path and were left on an incompatible version.

## Impact

- **Erigon DAppNode validators** missed part of the fork window (~2 hours of downtime during resync).
- **Geth DAppNode validators** had no working Pectra-compatible release and were unprotected at fork time.
- **Scope**: Gnosis has a meaningful share of home stakers running via DAppNode (~10%+). The affected validators represented a non-trivial portion of the network's stake during the transition.
- **No consensus failure**: The fork itself activated successfully. The impact was limited to reduced participation from affected DAppNode validators.

## Root Causes

1. **No ownership of DAppNode packages by Gnosis core team.** The team could not push updates to DAppNode packages directly. This dependency on external maintainers introduced delays and removed control over the upgrade timeline.

2. **No advance testing of DAppNode upgrade paths.** Each client's DAppNode upgrade path was not tested ahead of the fork. The Erigon full-resync requirement and Geth CI failure were discovered too late to mitigate.

3. **No DAppNode-specific upgrade guide.** No runbook or step-by-step guide was prepared in advance for DAppNode operators covering each supported client combination.

4. **Late client releases.** Some Pectra-compatible client versions landed very close to the fork date (Nethermind one week before, Erigon requiring a major version migration), leaving minimal margin for testing and coordination.

## Action Items for Fulu

1. **Claim ownership of all Gnosis DAppNode packages now.** Do not wait until fork time. Assign an owner from the Gnosis core team for each package and verify push access.

2. **Add DAppNode package updates to the fork prep checklist at least 2 weeks before fork date.** Packages should be updated, tested, and published well in advance -- not the week of the fork.

3. **Flag full-resync requirements 4 weeks in advance.** For any client requiring a full resync (e.g. major version bumps like Erigon v2 to v3), communicate this to validators at least 4 weeks before fork activation with a step-by-step migration guide. Validators need time to resync without missing the fork window.

4. **Require CI-passing, fork-compatible builds from all clients at least 1 week before fork.** Any client without a working build 1 week out should be flagged as at-risk and communicated to operators with fallback instructions.

5. **Create a DAppNode-specific upgrade runbook.** Cover every supported EL/CL client combination. Test the runbook on Chiado before mainnet fork activation.

6. **Add DAppNode validator participation rate to post-fork monitoring.** Include a "DAppNode validator participation rate" metric in the post-fork monitoring checklist to catch similar issues in real time.

## What Went Well

- **Most CL clients were ready on time.** Lighthouse, Teku, Nimbus, and Lodestar all had Pectra-compatible releases available well before the fork.
- **Nethermind was ready.** Despite the release landing one week before the fork, it was functional and available.
- **Reth was ready** (one PR merge away from full compatibility).
- **Fork activated successfully.** Despite the DAppNode issues, the Pectra hard fork activated without a consensus failure on Gnosis mainnet.
- **Communication was timely.** Coordination via Discord and Twitter kept operators informed about the situation and manual update steps.

## References

- [Core devs call, Mar 12, 2025](https://docs.gnosischain.com/updates/2025/03/12/core-devs-call)
- [Core devs call, Apr 23, 2025](https://docs.gnosischain.com/updates/2025/04/23/core-devs-call)
- [Pectra upgrade specification](https://github.com/gnosischain/specs/blob/master/network-upgrades/pectra.md)
- [Schedule Pectra PR #74](https://github.com/gnosischain/specs/pull/74)
