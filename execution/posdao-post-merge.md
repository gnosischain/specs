# POSDAO post-merge

[POSDAO](https://github.com/poanetwork/posdao-contracts) (Proof of Stake Decentralized Autonomous Organization consensus) is a DPOS consensus implemented in Solidity and running within EVM that drives the consensus of Gnosis chain up until the merge.

All POSDAO components are de-activated after the merge transition block except the capability to mint native tokens in response to events from the `erc-to-native` bridge.


## Specification

| Name | Value |
| - | - |
| `BLOCK_REWARD_CONTRACT` | `0x481c034c6d9441db23Ea48De68BCAe812C5d39bA` |
| `SYSTEM_SENDER`         | `0xfffffffffffffffffffffffffffffffffffffffe` |

Beginning with the merge transition block, execution clients **MUST** include the following payload validation and processing:

- System-level operation: block rewards call

**State transition**

The `reward` function of the `BlockRewardAuRa` contract MUST be called by with a [system call](#system-call) when producing and closing a block **after** any user-level transactions are applied. 

The implementation must construct and execute one system EVM transaction as follows:

```
sender: SYSTEM_SENDER
max_priority_fee_per_gas: 0
max_fee_per_gas: 0
gas_limit: 18446744073709551615
destination: BLOCK_REWARD_CONTRACT
amount: 0
payload: PAYLOAD
```

System transactions rules are:

- Gas limit checks are disabled compared to `block.gas_limit - block.gas_used` ([ref](https://github.com/NethermindEth/nethermind/blob/master/src/Nethermind/Nethermind.Evm/TransactionProcessing/TransactionProcessor.cs#L204-L220)).
- Caller balance and nonce checks are disabled. Nonce for system address is not incremented ([ref_1](https://github.com/NethermindEth/nethermind/blob/master/src/Nethermind/Nethermind.Evm/TransactionProcessing/TransactionProcessor.cs#L256-L287), [ref_2](https://github.com/NethermindEth/nethermind/blob/master/src/Nethermind/Nethermind.Evm/TransactionProcessing/TransactionProcessor.cs#L468-L471)).
- Fees are not added ([ref](https://github.com/NethermindEth/nethermind/blob/master/src/Nethermind/Nethermind.Evm/TransactionProcessing/TransactionProcessor.cs#L421-L448))
- `block.gas_used` is not incremented ([ref](https://github.com/NethermindEth/nethermind/blob/master/src/Nethermind/Nethermind.Evm/TransactionProcessing/TransactionProcessor.cs#L482-L485))
- If the transaction reverts, or runs out of the gas, the entire block **MUST** be considered invalid.


`PAYLOAD` is the ABI encoded arguments for a solidity function with ABI:

```solidity
function reward(
    address[] benefactors,
    uint16[] kind
) returns(
    address[] receiversNative,
    uint256[] memory rewardsNative
)
```

_[contracts/base/BlockRewardAuRaBase.sol](https://github.com/poanetwork/posdao-contracts/blob/0315e8ee854cb02d03f4c18965584a74f30796f7/contracts/base/BlockRewardAuRaBase.sol#L234)_

Where arguments MUST equal to a 1 element list with a single `benefactor` equal to `header.Coinbase` and a single kind of type 0 `RewardAuthor`.

```
rewards_call_data = abi_encode("reward", [header.coinbase], [0])
```

The return values of the system call are two lists of equal length. For each tuple item `(receiverNative, rewardNative)` the balance of `receiverNative` must be increased by `rewardNative`. The returned list may be empty. In case of overflow the block MUST be considered invalid.

