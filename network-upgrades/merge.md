# The Merge Upgrade Specification

## Included EIPs

This hard fork activates all EIPs also activated on Ethereum mainnet. There is however one addition and one change to an EIP, detailed below.

- [x] [EIP-3675](https://eips.ethereum.org/EIPS/eip-3675): Upgrade consensus to Proof-of-Stake (\*)
- [x] [EIP-4399](https://eips.ethereum.org/EIPS/eip-4399): Supplant DIFFICULTY opcode with PREVRANDAO

\* See [Differences with Ethereum mainnet](#differences-with-ethereum-mainnet)

## Differences with Ethereum mainnet

### [EIP-3675](https://eips.ethereum.org/EIPS/eip-3675)

This EIP has been adapted for Gnosis. More details TBA.

## Upgrade Schedule

| Network | TTD                                            | Date & Time (UTC) | Fork Hash | Beacon Chain Epoch |
| ------- | ---------------------------------------------- | ----------------- | --------- | ------------------ |
| Chiado  | 231707791542740786049188744689299064356246512  | ~ Nov 4, 2022     | -         | 180                |
| Mainnet | 8626000000000000000000058750000000000000000000 | ~ Dec 5, 2022     | -         | 385536             |

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
