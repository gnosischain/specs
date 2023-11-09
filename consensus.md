# Gnosis Beacon Chain specifications

Gnosis Beacon Chain follows the [Ethereum Proof-of-Stake consensus specifications](https://github.com/ethereum/consensus-specs) with different preset values. See [_Separation of Constant, Preset and Configuration variables #2390_](https://github.com/ethereum/consensus-specs/pull/2390) as definition of a preset versus a regular chain config.

Refer to [gnosischain/configs/mainnet/config.yaml](https://github.com/gnosischain/configs/blob/main/mainnet/config.yaml) for the chain's full config.

Note that modified preset values will result in different SSZ data structures, such that a client compiled with the Ethereum mainnet preset can't deserialize a state from the Gnosis Beacon Chain.

```
ETHEREUM_SPEC_COMMIT: v1.4.0-beta.4
```

### Preset diff

| Name                                   | Ethereum spec | Gnosis spec |
| -------------------------------------- | ------- | ------ |
| `BASE_REWARD_FACTOR`                   | `64`    | `25`   |
| `SLOTS_PER_EPOCH`                      | `32`    | `16`   |
| `EPOCHS_PER_SYNC_COMMITTEE_PERIOD`     | `256  ` | `512`  |
| `MAX_VALIDATORS_PER_WITHDRAWALS_SWEEP` | `16384` | `8192` |
| `MAX_WITHDRAWALS_PER_PAYLOAD`          | `16`    | `8`    |

### Config diff

| Name                                 | Ethereum spec | Gnosis spec  | 
| ------------------------------------ | ------------- | ------------ |
| `PRESET_BASE`                        | `mainnet`     | `gnosis` |
| `CHURN_LIMIT_QUOTIENT`               | `65536`       | `4096`       |
| `SECONDS_PER_SLOT`                   | `12`          | `5`          |
| `SECONDS_PER_ETH1_BLOCK`             | `14`          | `6`          |
| `ETH1_FOLLOW_DISTANCE`               | `2048`        | `1024`       |
| `TERMINAL_TOTAL_DIFFICULTY`          | `58750000000000000000000` | `8626000000000000000000058750000000000000000000` |
| `MAX_PER_EPOCH_ACTIVATION_CHURN_LIMIT` | `8`         | `2` |
| `MIN_EPOCHS_FOR_BLOB_SIDECARS_REQUESTS` | `4096`     | `16384` |

