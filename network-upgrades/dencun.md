# Dencun Upgrade Specification

## Included EIPs

This hard fork activates all EIPs also activated on Ethereum mainnet, [hard-fork EIP](https://eips.ethereum.org/EIPS/eip-7569).
Table below list differences if any.

| EIP | Scope |   |
| - | - | - |
| [EIP-1153](https://eips.ethereum.org/EIPS/eip-1153): Transient storage opcodes                | EL     | Not modified
| [EIP-4788](https://eips.ethereum.org/EIPS/eip-4788): Beacon block root in the EVM             | CL, EL | Not modified, same addresses as Ethereum
| [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844): Shard Blob Transactions                  | CL, EL | Constants maybe modified from Ethereum (* )
| [EIP-5656](https://eips.ethereum.org/EIPS/eip-5656): MCOPY - Memory copying instruction       | EL     | Not modified
| [EIP-6780](https://eips.ethereum.org/EIPS/eip-6780): SELFDESTRUCT only in same transaction    | EL     | Not modified
| [EIP-7044](https://eips.ethereum.org/EIPS/eip-7044): Perpetually Valid Signed Voluntary Exits | CL     | Not modified
| [EIP-7045](https://eips.ethereum.org/EIPS/eip-7045): Increase max attestation inclusion slot  | CL     | Not modified
| [EIP-7514](https://eips.ethereum.org/EIPS/eip-7514): Add Max Epoch Churn Limit                | CL     | Constants maybe modified from Ethereum (* )
| [EIP-7516](https://eips.ethereum.org/EIPS/eip-7516): BLOBBASEFEE opcode                       | EL     | Not modified

\* See [Differences with Ethereum mainnet](#differences-with-ethereum-mainnet)

Note: The trusted setup required for [deneb's cryptography](https://github.com/ethereum/consensus-specs/blob/dev/specs/deneb/polynomial-commitments.md#trusted-setup) is the same as defined in Ethereum's consensus spec release v1.4.0, which can be found in [consensus/preset/gnosis/trusted_setups](./consensus/preset/gnosis/trusted_setups/trusted_setup_4096.json).

## Differences with Ethereum mainnet

### [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844)

Gnosis chain has slots significantly faster than Ethereum. Bigger blocks _could_ have a higher cost to the network than Ethereum so we may price blobs differently. Ethereum mainnet has chosen a target of 3 blobs from real live experiments on mainnet with big blocks. Consecuently this parameters may not be adecuate.

Gnosis chain has significantly cheaper fees than mainnet, so blob spam is a concern. Ethereum's `MIN_BLOB_GASPRICE` makes blob space free (1e-18 USD / blob) if usage is under the target for a sustained period of time. The same concern applies to Ethereum, but consensus is that choosing a specific value that may apply to only some market conditions and not others. Given that Gnosis native token is a stable coin, this concerns are mitigated. Given usage under target for regular txs and blob data, setting min blob gas price to 1 GWei reduces the cost per byte by a factor of 16.

| Constant | Value |
| -------- | ----- |
| MIN_BLOB_GASPRICE | 1000000000 |
| TARGET_BLOB_GAS_PER_BLOCK | 131072 |
| MAX_BLOB_GAS_PER_BLOCK | 262144 |
| BLOB_GASPRICE_UPDATE_FRACTION | 1112826 |

### [EIP-7514](https://eips.ethereum.org/EIPS/eip-7514)

Gnosis chain has both a lower `CHURN_LIMIT_QUOTIENT` and faster epoch times. A `MAX_PER_EPOCH_ACTIVATION_CHURN_LIMIT` value of 2 provides a good trade-off to:
- Limit max state growth in the next year to 1M validators
- Increase the minimum time for a 2/3 malicious take-over to 150 days at current validator set sizes
- Allow validator set growth to prevent long queues unless there's exceptional demand

See https://hackmd.io/@5qNKk0aeQlygax4hX3rVXw/SJfbSY-ep for more details

| Constant | Value |
| -------- | ----- |
| MAX_PER_EPOCH_ACTIVATION_CHURN_LIMIT | 2 |

## Upgrade Schedule

| Network | Timestamp    | Date & Time (UTC)             | Fork Hash | Beacon Chain Epoch |
| ------- | ------------ | ----------------------------- | --------- | ------------------ |
| Chiado  | 1706724940 | Jan-31-2024 18:15:40 +UTC | -     | 516608           |
| Mainnet | 1710181820 | Mar-11-2024 18:30:20 +UTC | -     |     889856        |

### Readiness Checklist

**List of outstanding items before deployment.**

- [x] Client Integration Testing
  - [x] Deploy a Client Integration Testnet
  - [x] Integration Tests
- [x] Select Fork Triggers
  - [x] Chiado
  - [x] Mainnet
- [x] Deploy Clients
- [x] Activate Fork
