# Pectra Upgrade Specification

## Included EIPs

This hard fork activates all EIPs also activated on Ethereum mainnet, [hard-fork EIP](https://eips.ethereum.org/EIPS/eip-7600).
Table below list differences if any.

| EIP | Scope |   |
| - | - | - |
| [EIP-2537](https://eips.ethereum.org/EIPS/eip-2537): Precompile for BLS12-381 curve operations | EL     | Not modified
| [EIP-2935](https://eips.ethereum.org/EIPS/eip-2935): Save historical block hashes in state     | EL     | Not modified
| [EIP-3074](https://eips.ethereum.org/EIPS/eip-3074): AUTH and AUTHCALL opcodes                 | EL     | Not modified
| [EIP-6110](https://eips.ethereum.org/EIPS/eip-6110): Supply validator deposits on chain        | EL     | Not modified
| [EIP-7002](https://eips.ethereum.org/EIPS/eip-7002): Execution layer triggerable exits         | EL     | Not modified, same addresses as Ethereum
| [EIP-7251](https://eips.ethereum.org/EIPS/eip-7251): Increase the MAX_EFFECTIVE_BALANCE        | CL     | Not modified
| [EIP-7549](https://eips.ethereum.org/EIPS/eip-7549): Move committee index outside Attestation  | CL     | Not modified

\* See [Differences with Ethereum mainnet](#differences-with-ethereum-mainnet)

Note: The trusted setup required for [deneb's cryptography](https://github.com/ethereum/consensus-specs/blob/dev/specs/deneb/polynomial-commitments.md#trusted-setup) is the same as defined in Ethereum's consensus spec release v1.4.0, which can be found in [consensus/preset/gnosis/trusted_setups](./consensus/preset/gnosis/trusted_setups/trusted_setup_4096.json).

## Differences with Ethereum mainnet

_TBA_

## Upgrade Schedule

| Network | Timestamp    | Date & Time (UTC)             | Fork Hash | Beacon Chain Epoch |
| ------- | ------------ | ----------------------------- | --------- | ------------------ |
| Chiado  |              |                               |           |                    |
| Mainnet |              |                               |           |                    |

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

