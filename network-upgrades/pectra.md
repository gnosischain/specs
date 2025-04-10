# Pectra Upgrade Specification

## Included EIPs

This hard fork activates all EIPs also activated on Ethereum mainnet, [hard-fork EIP](https://eips.ethereum.org/EIPS/eip-7600).
Table below list differences if any.

| EIP | Scope |   |
| - | - | - |
| [EIP-2537](https://eips.ethereum.org/EIPS/eip-2537): Precompile for BLS12-381 curve operations | EL     | Not modified
| [EIP-2935](https://eips.ethereum.org/EIPS/eip-2935): Save historical block hashes in state     | EL     | Not modified
| [EIP-6110](https://eips.ethereum.org/EIPS/eip-6110): Supply validator deposits on chain        | EL     | Not modified
| [EIP-7002](https://eips.ethereum.org/EIPS/eip-7002): Execution layer triggerable exits         | EL     | Not modified, same addresses as Ethereum
| [EIP-7251](https://eips.ethereum.org/EIPS/eip-7251): Increase the MAX_EFFECTIVE_BALANCE        | CL     | Not modified
| [EIP-7549](https://eips.ethereum.org/EIPS/eip-7549): Move committee index outside Attestation  | CL     | Not modified
| [EIP-7685](https://eips.ethereum.org/EIPS/eip-7685): General purpose execution layer requests  | Both   | Not modified
| [EIP-7691](https://eips.ethereum.org/EIPS/eip-7691): Blob throughput increase                  | Both   | Constants modified
| [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702): Set EOA account code                      | EL     | Not modified
| [EIP-7840](https://eips.ethereum.org/EIPS/eip-7840): Add blob schedule to EL config files      | EL     | Not modified
| [EIP-4844-pectra](https://eips.ethereum.org/EIPS/eip-4844): Collect Blob Gas Fee               | EL     | Added

\* See [Differences with Ethereum mainnet](#differences-with-ethereum-mainnet)

Note: The trusted setup required for [deneb's cryptography](https://github.com/ethereum/consensus-specs/blob/dev/specs/deneb/polynomial-commitments.md#trusted-setup) is the same as defined in Ethereum's consensus spec release v1.4.0, which can be found in [consensus/preset/gnosis/trusted_setups](./consensus/preset/gnosis/trusted_setups/trusted_setup_4096.json).

## Differences with Ethereum mainnet

### [EIP-7691](https://eips.ethereum.org/EIPS/eip-7691)

The blob gas schedule is kept equal to the Dencun hard-fork.

| Constant                             | Value |
| ------------------------------------ | ----- |
| MAX_BLOBS_PER_BLOCK_ELECTRA          | 2
| TARGET_BLOBS_PER_BLOCK_ELECTRA       | 1
| MAX_BLOB_GAS_PER_BLOCK               | 262144
| TARGET_BLOB_GAS_PER_BLOCK            | 131072
| BLOB_BASE_FEE_UPDATE_FRACTION_PRAGUE | 1112826

### [EIP-4844-pectra](https://eips.ethereum.org/EIPS/eip-4844)

Extends the modified Gnosis EIP-4844 as defined in the [dencun spec](../dencun.md) document. Starting at the fork timestamp, the blob base fee is collected instead of burned.

| Constant | Value |
| - | - |
| EIP4844_FEE_COLLECTOR | 0x6BBe78ee9e474842Dbd4AB4987b3CeFE88426A92 |

The actual `blob_fee` as calculated via `calc_blob_fee` is deducted from the sender balance before transaction execution and credited to the pre-defined address `EIP4844_FEE_COLLECTOR` as part of block processing. It is not refunded in case of transaction failure.

## Upgrade Schedule

| Network | Timestamp    | Date & Time (UTC)             | Fork Hash  | Beacon Chain Epoch |
| ------- | ------------ | ----------------------------- | ---------- | ------------------ |
| Chiado  | 1741254220   | Mar-06-2025 09:43:40 +UTC     | 0x8ba51786 | 948224             |
| Mainnet | 1746021820   | Apr-30-2025 14:03:40 +UTC     | 0x2f095d4a | 1337856            |

### Readiness Checklist

**List of outstanding items before deployment.**

- [x] Client Integration Testing
  - [x] Deploy a Client Integration Testnet
  - [x] Integration Tests
- [x] Select Fork Triggers
  - [x] Chiado
  - [x] Mainnet
- [ ] Deploy Clients
- [ ] Activate Fork

