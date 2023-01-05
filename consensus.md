# Gnosis Beacon Chain specifications

Gnosis Beacon Chain follows the [Ethereum Proof-of-Stake consensus specifications](https://github.com/ethereum/consensus-specs) with different preset values. See [_Separation of Constant, Preset and Configuration variables #2390_](https://github.com/ethereum/consensus-specs/pull/2390) as definition of a preset versus a regular chain config.

Refer to [gnosischain/configs/mainnet/config.yaml](https://github.com/gnosischain/configs/blob/main/mainnet/config.yaml) for the chain's full config.

Note that modified preset values will result in different SSZ data structures, such that a client compiled with the Ethereum mainnet preset can't deserialize a state from the Gnosis Beacon Chain.

### phase0

**Preset**

| Name                 | Value |
| -------------------- | ----- |
| `BASE_REWARD_FACTOR` | `25`  |
| `SLOTS_PER_EPOCH`    | `16`  |

**Config**

| Name                                 | Value                                        |
| ------------------------------------ | -------------------------------------------- |
| `SECONDS_PER_SLOT`                   | `5`                                          |
| `SECONDS_PER_ETH1_BLOCK`             | `6`                                          |
| `ETH1_FOLLOW_DISTANCE`               | `1024`                                       |
| `CHURN_LIMIT_QUOTIENT`               | `4096`                                       |
| `DEPOSIT_CHAIN_ID`                   | `100`                                        |
| `DEPOSIT_NETWORK_ID`                 | `100`                                        |
| `DEPOSIT_CONTRACT_ADDRESS`           | `0x0b98057ea310f4d31f2a452b414647007d1645d9` |
| `MIN_GENESIS_TIME`                   | `1638968400`                                 |
| `MIN_GENESIS_ACTIVE_VALIDATOR_COUNT` | `4096`                                       |
| `GENESIS_FORK_VERSION`               | `0x00000064`                                 |
| `GENESIS_DELAY`                      | `6000`                                       |

### altair

**Preset**

| Name                               | Value |
| ---------------------------------- | ----- |
| `EPOCHS_PER_SYNC_COMMITTEE_PERIOD` | `512` |

**Config**

| Name                  | Value        |
| --------------------- | ------------ |
| `ALTAIR_FORK_VERSION` | `0x01000064` |
| `ALTAIR_FORK_EPOCH`   | `512`        |

### bellatrix

**Config**

| Name                        | Value                                            |
| --------------------------- | ------------------------------------------------ |
| `BELLATRIX_FORK_VERSION`    | `0x02000064`                                     |
| `BELLATRIX_FORK_EPOCH`      | `385536`                                         |
| `TERMINAL_TOTAL_DIFFICULTY` | `8626000000000000000000058750000000000000000000` |
