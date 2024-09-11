# Istanbul Upgrade Specification

## Included EIPs

This hard fork activates all EIPs also activated on Ethereum mainnet [hard-fork EIP](https://eips.ethereum.org/EIPS/eip-1679).
Table below list differences if any.

| EIP |  |
| - | - |
| [EIP-152](https://eips.ethereum.org/EIPS/eip-152): Add BLAKE2 compression function `F` precompile | Not modified
| [EIP-1108](https://eips.ethereum.org/EIPS/eip-1108): Reduce alt_bn128 precompile gas costs | Not modifed
| [EIP-1283](https://eips.ethereum.org/EIPS/eip-1283): Net gas metering for SSTORE without dirty maps | **Re-enable** (legacy version disabled EIP in previous fork) |
| [EIP-1344](https://eips.ethereum.org/EIPS/eip-1344): ChainID opcode | Not modified
| [EIP-1706](https://eips.ethereum.org/EIPS/eip-1706): Disable SSTORE with gasleft lower than call stipend | Not modified
| [EIP-1884](https://eips.ethereum.org/EIPS/eip-1884): Repricing for trie-size-dependent opcodes | Not modified
| [EIP-2028](https://eips.ethereum.org/EIPS/eip-2028): Transaction data gas cost reduction | Not modified
| [EIP-2200](https://eips.ethereum.org/EIPS/eip-2200): Structured Definitions for Net Gas Metering | **Not included**

## Upgrade Schedule

| Network | Block   | Date & Time (UTC)             | 
| ------- | ------- | ----------------------------- | 
| Mainnet | 7298030 | Dec-12-2019 07:13:00 AM +UTC  | 

