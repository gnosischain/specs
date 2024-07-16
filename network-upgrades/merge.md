# The Merge Upgrade Specification

## Included EIPs

This hard fork activates all EIPs also activated on Ethereum mainnet, [paris specs](https://github.com/ethereum/execution-specs/blob/master/network-upgrades/mainnet-upgrades/paris.md).
Table below list differences if any.

| EIP | Scope |  |
| - | - | - |
| [EIP-3675](https://eips.ethereum.org/EIPS/eip-3675): Upgrade consensus to Proof-of-Stake | CL, EL | Modified
| [EIP-4399](https://eips.ethereum.org/EIPS/eip-4399): Supplant DIFFICULTY opcode with PREVRANDAO | EL | Not modified

## Differences with Ethereum mainnet

### [EIP-3675](https://eips.ethereum.org/EIPS/eip-3675)

This EIP has been adapted for Gnosis. More details TBA.

## Upgrade Schedule

| Network | TTD                                            | Date & Time (UTC) | Fork Hash | Beacon Chain Epoch |
| ------- | ---------------------------------------------- | ----------------- | --------- | ------------------ |
| Chiado  | 231707791542740786049188744689299064356246512  | ~ Nov 4, 2022     | -         | 180                |
| Mainnet | 8626000000000000000000058750000000000000000000 | Dec-08-2022 18:45:25 +UTC  | -         | 394147             |

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
