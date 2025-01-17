# Constantinople Upgrade Specification

## Included EIPs

This hard fork activates all EIPs also activated on Ethereum mainnet [hard-fork EIP](https://eips.ethereum.org/EIPS/eip-1013).
Table below list differences if any.

| EIP |  |
| - | - |
| [EIP-145](https://eips.ethereum.org/EIPS/eip-145:) Bitwise shifting instructions in EVM | Not modified |
| [EIP-1014](https://eips.ethereum.org/EIPS/eip-1014): Skinny CREATE2 | Not modified |
| [EIP-1052](https://eips.ethereum.org/EIPS/eip-1052): EXTCODEHASH opcode | Not modified |
| [EIP-1283](https://eips.ethereum.org/EIPS/eip-1283): Net gas metering for SSTORE without dirty maps | Different scheduling |

## Differences with Ethereum mainnet

### [EIP-1283](https://eips.ethereum.org/EIPS/eip-1283)

[EIP-1283](https://eips.ethereum.org/EIPS/eip-1283) activated in Gnosis Chain but it never activated in Ethereum. Latter stages of testing in Ethereum revealed issues that lead to the deprecation of the EIP. Gnosis Chain de-activated the EIP in a latter fork [Constantinople-B](../constantinople-b.md).

## Upgrade Schedule

| Network | Block   | Date & Time (UTC)             | Fork Hash | 
| ------- | ------- | ----------------------------- | --------- | 
| Mainnet | 1604400 | Jan-11-2019 11:24:50 AM +UTC  | 0xfde2d083 | 

