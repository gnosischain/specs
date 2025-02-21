# Gnosis Beacon Chain specifications

Gnosis Beacon Chain follows the [Ethereum Proof-of-Stake consensus specifications](https://github.com/ethereum/consensus-specs) with different preset values. See [_Separation of Constant, Preset and Configuration variables #2390_](https://github.com/ethereum/consensus-specs/pull/2390) as definition of a preset versus a regular chain config.

Refer to [./consensus/config/gnosis.yaml](./consensus/config/gnosis.yaml) for the chain's full config.

Note that modified preset values will result in different SSZ data structures, such that a client compiled with the Ethereum mainnet preset can't deserialize a state from the Gnosis Beacon Chain.

```
ETHEREUM_SPEC_COMMIT: v1.5.0-alpha.10
```

### Preset diff

| Name                                   | Ethereum spec | Gnosis spec |
| -------------------------------------- | ------- | ------ |
| `BASE_REWARD_FACTOR`                   | `64`    | `25`   |
| `SLOTS_PER_EPOCH`                      | `32`    | `16`   |
| `EPOCHS_PER_SYNC_COMMITTEE_PERIOD`     | `256`   | `512`  |
| `MAX_VALIDATORS_PER_WITHDRAWALS_SWEEP` | `16384` | `8192` |
| `MAX_WITHDRAWALS_PER_PAYLOAD`          | `16`    | `8`    |

### Config diff

| Name                                    | Ethereum spec | Gnosis spec  |   |
| --------------------------------------- | ------------- | ------------ | - |
| `CHURN_LIMIT_QUOTIENT`                  | `65536`       | `4096`       |
| `SECONDS_PER_SLOT`                      | `12`          | `5`          |
| `SECONDS_PER_ETH1_BLOCK`                | `14`          | `6`          |
| `ETH1_FOLLOW_DISTANCE`                  | `2048`        | `1024`       |
| `MAX_PER_EPOCH_ACTIVATION_CHURN_LIMIT`  | `8`           | `2`          | See https://github.com/gnosischain/specs/pull/22 for rationale |
| `MIN_EPOCHS_FOR_BLOB_SIDECARS_REQUESTS` | `4096`        | `16384`      | Increased to match the expected 2 weeks rollups consider today for Ethereum mainnet. The total disk requirement roughly equivalent to Ethereum mainnet since epochs are 4.8x faster |
| `MAX_BLOBS_PER_BLOCK`                   | `6`           | `2`          | See [/network-upgrades/dencun.md#eip-4844](/network-upgrades/dencun.md#eip-4844) for rationale on choosing 1/2 for the Dencun hard fork |
| `MAX_PER_EPOCH_ACTIVATION_EXIT_CHURN_LIMIT` | `256000000000` | `64000000000` | Match the modified value `MAX_PER_EPOCH_ACTIVATION_CHURN_LIMIT` https://github.com/gnosischain/specs/pull/22 for rationale |
| `MAX_BLOBS_PER_BLOCK_ELECTRA`           | `9`           | `2`          | Temporary value equal to `MAX_BLOBS_PER_BLOCK` |
| `MAX_BLOBS_PER_BLOCK_FULU`              | `12`          | `2`          | Temporary value equal to `MAX_BLOBS_PER_BLOCK` |

