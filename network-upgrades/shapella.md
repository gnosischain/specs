# Shapella Upgrade Specification

## Included EIPs

This hard fork activates all EIPs also activated on Ethereum mainnet, [shanghai specs](https://github.com/ethereum/execution-specs/blob/master/network-upgrades/mainnet-upgrades/shanghai.md).
Table below list differences if any.

| EIP | Scope |  |
| - | - | - |
| [EIP-170](https://eips.ethereum.org/EIPS/eip-170): Contract code size limit | EL | [**Different scheduling**](#eip-170) (at a latter fork than Ethereum)
| [EIP-3651](https://eips.ethereum.org/EIPS/eip-3651): Warm COINBASE | EL | Not modified
| [EIP-3855](https://eips.ethereum.org/EIPS/eip-3855): PUSH0 instruction | EL | Not modified
| [EIP-3860](https://eips.ethereum.org/EIPS/eip-3860): Limit and meter initcode | EL | Not modified
| [EIP-4895](https://eips.ethereum.org/EIPS/eip-4895): Beacon chain push withdrawals as operations | CL, EL | [**Modified**](#eip-4895)
| [EIP-6049](https://eips.ethereum.org/EIPS/eip-6049): Deprecate SELFDESTRUCT | EL | Not modified

## Differences with Ethereum mainnet

### [EIP-170](https://eips.ethereum.org/EIPS/eip-170)

This EIP was enabled on the Spurious Dragon hard fork on Ethereum, and wasn't enabled on Gnosis before the Shapella hard fork. The Shapella hard fork for Gnosis activates this EIP as it's a requirement for [EIP-3860](https://eips.ethereum.org/EIPS/eip-3860).

### [EIP-4895](https://eips.ethereum.org/EIPS/eip-4895)

This EIP has been adapted for Gnosis. More details in [`/execution/withdrawals.md`](../execution/withdrawals.md).

## Upgrade Schedule

| Network | Timestamp    | Date & Time (UTC)             | Fork Hash | Beacon Chain Epoch |
| ------- | ------------ | ----------------------------- | --------- | ------------------ |
| Chiado  | `1684934220` | May-24-2023 13:17:00 +UTC | 0xa15a4252 | 244224             |
| Mainnet | `1690889660` | Aug-01-2023 11:34:20 +UTC | 0x2efe91ba | 648704             |

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
