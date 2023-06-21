# Shapella Upgrade Specification

## Included EIPs

This hard fork activates all EIPs also activated on Ethereum mainnet. There is however one addition and one change to an EIP, detailed below.

- [EIP-170](https://eips.ethereum.org/EIPS/eip-170): Contract code size limit. Activated in Gnosis at a latter fork than Ethereum (\*)
- [EIP-3651](https://eips.ethereum.org/EIPS/eip-3651): Warm COINBASE. Makes it a bit less expensive to access the coinbase address. Useful for flashbots for example
- [EIP-3855](https://eips.ethereum.org/EIPS/eip-3855): PUSH0 instruction. Slight gas optimization when pushing a 0 to the stack
- [EIP-3860](https://eips.ethereum.org/EIPS/eip-3860): Limit and meter initcode. Limits the size of deployed contracts and makes deployments a bit more expensive
- [EIP-4895](https://eips.ethereum.org/EIPS/eip-4895): Beacon chain push withdrawals as operations (\*)
- [EIP-6049](https://eips.ethereum.org/EIPS/eip-6049): Deprecate SELFDESTRUCT. Deprecates the SELFDESTRUCT opcode. Doesn’t actually change its behavior yet

\* See [Differences with Ethereum mainnet](#differences-with-ethereum-mainnet)

## Differences with Ethereum mainnet

### [EIP-170](https://eips.ethereum.org/EIPS/eip-170)

This EIP was enabled on the Spurious Dragon hard fork on Ethereum, and wasn't enabled on Gnosis before the Shapella hard fork. The Shapella hard fork for Gnosis activates this EIP as it's a requirement for [EIP-3860](https://eips.ethereum.org/EIPS/eip-3860).

### [EIP-4895](https://eips.ethereum.org/EIPS/eip-4895)

This EIP has been adapted for Gnosis. More details in [`/execution/withdrawals.md`](../execution/withdrawals.md).

## Upgrade Schedule

| Network | Timestamp    | Date & Time (UTC)             | Fork Hash | Beacon Chain Epoch |
| ------- | ------------ | ----------------------------- | --------- | ------------------ |
| Chiado  | `1684934220` | May 24 2023 13:17:00 GMT+0000 | -         | 244224             |
| Mainnet | `1690889660` | Aug 01 2023 11:34:20 GMT+0000 | -         | 648704             |

### Implementation Progresss

Implementation status of Included & CFI'd EIPs across participating clients.

| EIP                                    | **Nethermind** | **Erigon** |
| -------------------------------------- | -------------- | ---------- |
| [EIP-4895](./execution/withdrawals.md) | -              | -          |

### Readiness Checklist

**List of outstanding items before deployment.**

- [x] Client Integration Testing
  - [x] Deploy a Client Integration Testnet
  - [x] Integration Tests
- [ ] Select Fork Triggers
  - [x] Chiado
  - [ ] Mainnet
- [ ] Deploy Clients
- [ ] Activate Fork
