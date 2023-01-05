# Gnosis Beacon Chain specifications

Gnosis Beacon Chain follows the [Ethereum Proof-of-Stake consensus specifications](https://github.com/ethereum/consensus-specs) with different preset values. See [_Separation of Constant, Preset and Configuration variables #2390_](https://github.com/ethereum/consensus-specs/pull/2390) as definition of a preset versus a regular chain config.

Note that modified preset values will result in different SSZ data structures, such that a client compiled with the Ethereum mainnet preset can't deserialize a state from the Gnosis Beacon Chain.

### phase0

| Name                 | Value |
| -------------------- | ----- |
| `BASE_REWARD_FACTOR` | `25`  |
| `SLOTS_PER_EPOCH`    | `16`  |

### altair

| Name                               | Value |
| ---------------------------------- | ----- |
| `EPOCHS_PER_SYNC_COMMITTEE_PERIOD` | `512` |

### bellatrix

None
