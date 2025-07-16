# Fusaka Upgrade Specification

## Included EIPs

This hard fork activates all EIPs also activated on Ethereum mainnet, [hard-fork EIP](https://eips.ethereum.org/EIPS/eip-7607).
Table below list differences if any.

| EIP | Scope |   |
| - | - | - |
| [EIP-7594](https://eips.ethereum.org/EIPS/eip-7594): PeerDAS - Peer Data Availability Sampling   | Both | Not modified
| [EIP-7823](https://eips.ethereum.org/EIPS/eip-7823): Set upper bounds for MODEXP                 | EL   | Not modified
| [EIP-7825](https://eips.ethereum.org/EIPS/eip-7825): Transaction Gas Limit Cap                   | EL   | Not modified
| [EIP-7883](https://eips.ethereum.org/EIPS/eip-7883): ModExp Gas Cost Increase                    | EL   | Not modified
| [EIP-7892](https://eips.ethereum.org/EIPS/eip-7892): Blob Parameter Only Hardforks               | Both | [**Modified constants**](#eip-7892)
| [EIP-7907](https://eips.ethereum.org/EIPS/eip-7907): Meter Contract Code Size And Increase Limit | EL   | Not modified
| [EIP-7917](https://eips.ethereum.org/EIPS/eip-7917): Deterministic proposer lookahead            | CL   | Not modified
| [EIP-7918](https://eips.ethereum.org/EIPS/eip-7918): Blob base fee bounded by execution cost     | EL   | Not modified
| [EIP-7934](https://eips.ethereum.org/EIPS/eip-7934): RLP Execution Block Size Limit              | EL   | Not modified
| [EIP-7935](https://eips.ethereum.org/EIPS/eip-7935): Set default gas limit to XX0M               | EL   | [**Modified constants**](#eip-7935)
| [EIP-7939](https://eips.ethereum.org/EIPS/eip-7939): Count leading zeros (CLZ) opcode            | EL   | Not modified
| [EIP-7951](https://eips.ethereum.org/EIPS/eip-7951): Precompile for secp256r1 Curve Support      | EL   | Not modified

\* See [Differences with Ethereum mainnet](#differences-with-ethereum-mainnet)


## Differences with Ethereum mainnet

### [EIP-7892](https://eips.ethereum.org/EIPS/eip-7892)

Gnosis chain intends to sets a different blob target and max schedule than Ethereum, TBD.

### [EIP-7935](https://eips.ethereum.org/EIPS/eip-7935)

Gnosis chain intends to sets a different gas limit than Ethereum, TBD.

## Upgrade Schedule

| Network | Timestamp    | Date & Time (UTC)             | Fork Hash  | Beacon Chain Epoch |
| ------- | ------------ | ----------------------------- | ---------- | ------------------ |
| Chiado  | -            | -                             | -          | -                  |
| Mainnet | -            | -                             | -          | -                  |

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


