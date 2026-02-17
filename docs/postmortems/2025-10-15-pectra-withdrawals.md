# Post-Mortem: Pectra Withdrawals Bug on Gnosis Chain

**Date**: October 15, 2025
**Severity**: Critical (consensus-layer vulnerability)
**Networks affected**: Gnosis Chiado (triggered), Gnosis Mainnet (vulnerable, not triggered)
**Ethereum impact**: None

## Summary

A bug in the Electra spec's `get_expected_withdrawals()` caused a consensus split on Gnosis Chiado. Gnosis configures `MAX_PENDING_PARTIALS_PER_WITHDRAWALS_SWEEP` and `MAX_WITHDRAWALS_PER_PAYLOAD` to the same value (8), violating an implicit spec invariant. This allowed blocks with more withdrawals than the maximum, causing client disagreement.

Gnosis mainnet was vulnerable but the bug was never triggered. The issue was resolved by privately distributing client builds with a reduced `MAX_PENDING_PARTIALS_PER_WITHDRAWALS_SWEEP` to operators before exploitation on mainnet.

## Timeline

- **Oct 15, 2025 02:10 UTC** &mdash; Bug triggered on Chiado at [slot 19019584](https://beacon.chiadochain.net/slot/19019584). Blocks with 9 withdrawals (exceeding `MAX_WITHDRAWALS_PER_PAYLOAD = 8`) cause a chain split. Triggered by scripted partial withdrawal activity from a large staking provider.
- **Oct 15, 2025 ~07:14 UTC** &mdash; Issue escalated to Ethereum core dev channels.
- **Oct 15, 2025 ~07:25 UTC** &mdash; Root cause identified. No reference test can catch this under standard presets.
- **Oct 15, 2025 ~08:34 UTC** &mdash; Gnosis mainnet confirmed vulnerable given the right sequence of partial withdrawal requests.
- **Oct 15, 2025 ~08:49 UTC** &mdash; Core devs lean toward a Gnosis preset change to avoid risk to Ethereum.
- **Oct 15, 2025 ~10:16 UTC** &mdash; Chiado declared non-recoverable.
- **Oct 15, 2025 ~10:49 UTC** &mdash; Agreement on remediation: private client images with reduced preset, fold change into Fulu scheduling, post-mortem after Fulu.
- **Oct 15, 2025 ~16:23 UTC** &mdash; Max observed partial withdrawals per block on mainnet is 3. Private docker images for Teku, Lodestar, and Nimbus built with `MAX_PENDING_PARTIALS_PER_WITHDRAWALS_SWEEP` set to 6. Rollout to operators begins.

## Root Cause

### The Gnosis preset configuration

| Constant | Gnosis | Ethereum |
| --- | --- | --- |
| `MAX_WITHDRAWALS_PER_PAYLOAD` | **8** | 16 |
| `MAX_PENDING_PARTIALS_PER_WITHDRAWALS_SWEEP` | **8** | 8 |

On Ethereum, `MAX_PENDING_PARTIALS_PER_WITHDRAWALS_SWEEP` (8) is strictly less than `MAX_WITHDRAWALS_PER_PAYLOAD` (16), so the pending partial withdrawals loop can never fill the payload. On Gnosis both values are 8, exposing a latent bug.

### The spec bug

[`get_expected_withdrawals()`](https://github.com/ethereum/consensus-specs/blob/aae5237f01e50bef13459a88b4b28f1acceb67b1/specs/electra/beacon-chain.md) has two sequential loops:

1. **Pending partial withdrawals loop**: appends withdrawals until `len(withdrawals) == MAX_PENDING_PARTIALS_PER_WITHDRAWALS_SWEEP`.
2. **Validator sweep loop**: appends withdrawals until `len(withdrawals) == MAX_WITHDRAWALS_PER_PAYLOAD`.

The break condition in the sweep loop is at the **bottom**, after appending:

```python
for _ in range(bound):
    validator = state.validators[validator_index]
    # ... check conditions and append withdrawal ...

    if len(withdrawals) == MAX_WITHDRAWALS_PER_PAYLOAD:  # <-- after append
        break
    validator_index = ValidatorIndex((validator_index + 1) % len(state.validators))
```

When the first loop already produced 8 withdrawals (`== MAX_WITHDRAWALS_PER_PAYLOAD`), the sweep loop appends a 9th **before** checking the break. This exceeds `MAX_WITHDRAWALS_PER_PAYLOAD` and produces an invalid block.

### Secondary issue: sweep pointer reset

In `process_withdrawals()`, `next_withdrawal_validator_index` is derived from the last withdrawal:

```python
if len(expected_withdrawals) == MAX_WITHDRAWALS_PER_PAYLOAD:
    next_validator_index = ValidatorIndex(
        (expected_withdrawals[-1].validator_index + 1) % len(state.validators)
    )
    state.next_withdrawal_validator_index = next_validator_index
else:
    next_index = state.next_withdrawal_validator_index + MAX_VALIDATORS_PER_WITHDRAWALS_SWEEP
    state.next_withdrawal_validator_index = ValidatorIndex(next_index % len(state.validators))
```

When all slots are consumed by pending partials with no sweep withdrawals, the pointer resets to the last partial withdrawal validator instead of advancing the sweep, causing withdrawal liveness issues.

### Existing invariant (not enforced at runtime)

The spec test suite included an [invariant test](https://github.com/ethereum/consensus-specs/blob/aae5237f01e50bef13459a88b4b28f1acceb67b1/tests/core/pyspec/eth2spec/test/electra/unittests/test_config_invariants.py#L12) asserting `MAX_PENDING_PARTIALS_PER_WITHDRAWALS_SWEEP < MAX_WITHDRAWALS_PER_PAYLOAD`. However, clients did not enforce this when loading presets. Ethereum's minimal and mainnet presets satisfy it; the Gnosis preset does not.

## Impact

### Chiado testnet

- Clients disagreed on block validity, causing a consensus split.
- **Teku** produced blocks with 0 withdrawals (internal truncation to SSZ `List` limit).
- **Lighthouse** truncated `get_expected_withdrawals` output, masking the overflow but diverging from other clients.
- Network became non-recoverable and was allowed to die.

### Gnosis mainnet

- Vulnerable but not triggered. Max observed pending partials per block was 3. An attacker could have submitted enough partial withdrawal requests to fill all 8 slots and trigger the bug.
- Griefing vector: pending partials could exhaust all withdrawal slots, preventing the validator sweep entirely.

### Ethereum

- Not affected. Presets satisfy the invariant.

## Resolution

### Immediate (October 15, 2025)

1. **Private preset change**: Docker images for Teku, Lodestar, and Nimbus built with `MAX_PENDING_PARTIALS_PER_WITHDRAWALS_SWEEP` reduced from 8 to 6.
2. **Coordinated rollout**: Images distributed to operators through private channels before publicizing the vulnerability.
3. **Chiado abandoned**.

### Long-term

1. **Public preset change with Fulu**: Reduced value included in the Fulu hard fork scheduling on Gnosis.
2. **Optional upstream spec fix**: [Proposed by Justin Traglia](https://github.com/ethereum/consensus-specs/compare/master...jtraglia:consensus-specs:allow-no-sweep-withdrawals), deprioritized by Ethereum core devs as it does not affect Ethereum and carries nonzero regression risk.

## Client behavior summary

| Client | Behavior on overflow |
| --- | --- |
| Lighthouse | Truncated withdrawal list to SSZ `List` limit; mismatched expected withdrawals |
| Teku | Produced blocks with 0 withdrawals |
| Lodestar | Accepted blocks with > 8 withdrawals |
| Nimbus | Accepted blocks with > 8 withdrawals |

## Lessons Learned

1. **Config invariants must be enforced at runtime.** The spec test suite had the correct invariant, but no client enforced it when loading configurations. Clients should validate preset invariants at startup and refuse to run with invalid configurations.

2. **Alternative preset configurations are under-tested.** The Ethereum spec test suite generates reference tests only for `minimal` and `mainnet` presets. Gnosis uses a custom preset that violated an assumption holding for both standard presets. To address this, Gnosis is building out its own [consensus-specs fork](https://github.com/gnosischain/consensus-specs) that generates test vectors for the Gnosis preset, executed against clients via [hive](https://github.com/ethereum/hive).

## References

- [Electra `get_expected_withdrawals()` spec](https://github.com/ethereum/consensus-specs/blob/aae5237f01e50bef13459a88b4b28f1acceb67b1/specs/electra/beacon-chain.md)
- [Config invariant test in consensus-specs](https://github.com/ethereum/consensus-specs/blob/aae5237f01e50bef13459a88b4b28f1acceb67b1/tests/core/pyspec/eth2spec/test/electra/unittests/test_config_invariants.py#L12)
- [Proposed spec fix by Justin Traglia](https://github.com/ethereum/consensus-specs/compare/master...jtraglia:consensus-specs:allow-no-sweep-withdrawals)
- [Gnosis Electra preset](https://github.com/gnosischain/specs/blob/master/consensus/preset/gnosis/electra.yaml)
- [Gnosis Capella preset](https://github.com/gnosischain/specs/blob/master/consensus/preset/gnosis/capella.yaml)
- [Chiado block 19029534 (8 partial withdrawals)](https://beacon.chiadochain.net/slot/19029534)
