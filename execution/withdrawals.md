# Withdrawals

Support validator withdrawals from the beacon chain to the EVM via a "system-level" operation type.

## Motivation

Provide a way for beacon chain withdrawals to enter into the EVM. Extends [ethereum/eip-4895](https://eips.ethereum.org/EIPS/eip-4895) but instead of minting native tokens calls an predefined contract which disperses a non-native tokens.

## Specification

| Name                  | Value |
| --------------------- | ----- |
| `FORK_TIMESTAMP`      | `TBD` |
| `WITHDRAWAL_CONTRACT` | `TBD` |

Beginning with the execution timestamp `FORK_TIMESTAMP`, execution clients **MUST** introduce the following extensions to payload validation and processing:

The following sections of [ethereum/eip-4895](https://eips.ethereum.org/EIPS/eip-4895#system-level-operation-withdrawal) are implemented un-altered

- System-level operation: withdrawal
- New field in the execution payload: withdrawals
- New field in the execution payload header: withdrawals root
- Execution payload validity

**State transition**

The `withdrawals` in an execution payload are processed **after** any user-level transactions are applied.

For each `withdrawal` in the list of `execution_payload.withdrawals`, the implementation must construct and execute an EVM transaction as follows:

```
max_priority_fee_per_gas: TBD
max_fee_per_gas: TBD
gas_limit: TBD
destination: WITHDRAWAL_CONTRACT
amount: 0
payload: PAYLOAD
```

`PAYLOAD` is the ABI encoded arguments for a solidity function with ABI

```c#
function withdraw(uint256 amount, address address)
```

Where `amount` equals `withdrawal.amount` and `address` equals `withdrawal.address`.

If the transaction reverts, or runs out of the gas, the entire block **MUST** be considered invalid.

## Rationale

### Why does the EIP-4895 need to be modified?

Gnosis Beacon Chain stakes a non-native token (GNO), while Ethereum stakes its native token (ETH). Gnosis Chain native token (xDAI) must only be minted when bridging DAI from Ethereum mainnet, to mantain its 1:1 peg with Ethereum DAI tokens. This introduces the mandatory requirement to at least disable the state transition as defined in EIP-4895.

A withdrawal from the Gnosis Beacon Chain must trigger the release of GNO from an EVM contract. This can potentially be achieved at the consensus level with a system transaction as proposed here. However, since those tokens are already available at the EVM, it is possible to conditionally release them by proving to a contract that a withdrawal was included in a canonical block. Such a strategy would require constant upkeep, and given the expected rate of withdrawals it was deemed to risky and expensive.

### Why general EVM execution instead of just modifying storage?

Given that a transfer or ERC20 tokens is required, modifying the state directly would restrict the implementation of the withdrawal contract too much. Existing Gnosis Chain execution nodes already perform system level operations against the BlockRewards contract of POSDAO. So general EVM execution is consistent with the status quo.

## Backwards Compatibility

No issues

## Security Considerations

TBA
