# Dencun Upgrade Specification

## Included EIPs

This hard fork activates all EIPs also activated on [Ethereum mainnet](https://github.com/ethereum/execution-specs/blob/2a592a8268311bb6c28c8ca25ff8a35a74615127/network-upgrades/mainnet-upgrades/cancun.md#included-eips). Table below list differences if any.

| EIP |   |
| --- | - |
| [EIP-1153](https://eips.ethereum.org/EIPS/eip-1153): Transient storage opcodes             | Not modified
| [EIP-4788](https://eips.ethereum.org/EIPS/eip-4788): Beacon block root in the EVM          | Constants maybe modified from Ethereum (* )
| [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844): Shard Blob Transactions               | Constants maybe modified from Ethereum (* )
| [EIP-5656](https://eips.ethereum.org/EIPS/eip-5656): MCOPY - Memory copying instruction    | Not modified
| [EIP-6780](https://eips.ethereum.org/EIPS/eip-6780): SELFDESTRUCT only in same transaction | Not modified
| [EIP-7514](https://eips.ethereum.org/EIPS/eip-7514): Add Max Epoch Churn Limit             | Constants maybe modified from Ethereum (* )
| [EIP-7516](https://eips.ethereum.org/EIPS/eip-7516): BLOBBASEFEE opcode                    | Not modified

\* See [Differences with Ethereum mainnet](#differences-with-ethereum-mainnet)

## Differences with Ethereum mainnet

### [EIP-4788](https://eips.ethereum.org/EIPS/eip-4788)

The ring buffer data-structure is sized to expose at least a root that's 98304 seconds (1 day) old. This value is computed assuming 12 seconds per slot. Since Gnosis chain has faster slot times with 5 seconds per slot, this constants may have to be adjusted. Not changing the constant would increase the upper bound of roots stored in the contract, while exposing roots of the same age.

| Constant | Value |
| -------- | ----- |
| HISTORICAL_ROOTS_MODULUS | TBD |

### [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844)

Gnosis chain has slots significantly faster than Ethereum. Bigger blocks _could_ have a higher cost to the network than Ethereum so we may price blobs differently. Ethereum mainnet has chosen a target of 3 blobs from real live experiments on mainnet with big blocks. Consecuently this parameters may not be adecuate.

Gnosis chain has significantly cheaper fees than mainnet, so blob spam is a concern. Ethereum's `MIN_BLOB_GASPRICE` makes blob space free (1e-18 USD / blob) if usage is under the target for a sustained period of time. The same concern applies to Ethereum, but consensus is that choosing a specific value that may apply to only some market conditions and not others. Gnosis however has chosen a min gas price of 1 GWei, so a similar decision can be made here. 

| Constant | Value |
| -------- | ----- |
| MIN_BLOB_GASPRICE | TBD |
| TARGET_BLOB_GAS_PER_BLOCK | TBD |
| MAX_BLOB_GAS_PER_BLOCK | TBD |

### [EIP-7514](https://eips.ethereum.org/EIPS/eip-7514)

Gnosis chain has a custom `CHURN_LIMIT_QUOTIENT` config value, thus it should use a custom max churn limit.

| Constant | Value |
| -------- | ----- |
| MAX_PER_EPOCH_CHURN_LIMIT | TBD |

## Upgrade Schedule

| Network | Timestamp    | Date & Time (UTC)             | Fork Hash | Beacon Chain Epoch |
| ------- | ------------ | ----------------------------- | --------- | ------------------ |
| Chiado  | TBD | TBD | -         | TBD             |
| Mainnet | TBD | TBD | -         | TBD             |

### Implementation Progresss

Implementation status of Included & CFI'd EIPs across participating clients.

| EIP                                    | **Nethermind** | **Erigon** |
| -------------------------------------- | -------------- | ---------- |
| [EIP-4844](./execution/withdrawals.md) | -              | -          |

### Readiness Checklist

**List of outstanding items before deployment.**

- [ ] Client Integration Testing
  - [ ] Deploy a Client Integration Testnet
  - [ ] Integration Tests
- [ ] Select Fork Triggers
  - [ ] Chiado
  - [ ] Mainnet
- [ ] Deploy Clients
- [ ] Activate Fork
