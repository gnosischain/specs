# Balancer recovery

## Abstract

Introduce an irregular state transition on Gnosis Chain to replace the code of the Balancer V2 attacker’s externally owned account (EOA) with a restricted forwarding contract.
This enables coordinated recovery and subsequent redistribution of funds taken in the Balancer V2 exploit of November 3, 2025.

## Motivation

The attacker’s address `BALANCER_ATTACKER_ADDRESS` currently controls funds obtained in the Balancer V2 exploit of November 3, 2025, which affected composable stable pools across multiple chains including Gnosis Chain. 

Prior to this proposal, a majority of Gnosis Chain validators deployed a soft-fork level censorship rule to prevent any transaction from `BALANCER_ATTACKER_ADDRESS` from being included in blocks.
While this prevents the attacker from unilaterally moving funds, it does not in itself allow recovery or redistribution to affected parties.

An irregular state transition is therefore required so that:
- The attacker can no longer issue valid transactions from the compromised EOA (enforced by [EIP-3607](https://eips.ethereum.org/EIPS/eip-3607), and
- A designated recovery controller can safely execute scripted transfers from that address to recovery and redistribution contracts on Gnosis Chain.

## Specification

This specification introduces an irregular state transition on Gnosis Chain that sets the code of `BALANCER_ATTACKER_ADDRESS` to a fixed “hardcoded forwarder” contract, controlled by `BALANCER_RESCUE_ADDRESS`.

During block processing of the first block whose timestamp crosses `BALANCER_HARDFORK_TIMESTAMP`, and before the system calls of EIP-4788 and EIP-2935, the bytecode of account `BALANCER_ATTACKER_ADDRESS` **MUST** be set to `BALANCER_RESCUE_BYTECODE`.
No other account fields (balance, nonce, storage) are modified.

### Parameters

| Constant | Value |
| - | - |
| `BALANCER_HARDFORK_TIMESTAMP` | `1766419900` |
| `BALANCER_ATTACKER_ADDRESS` | `0x506d1f9efe24f0d47853adca907eb8d89ae03207` |
| `BALANCER_RESCUE_ADDRESS`   | `0x7Be579238a6a621601Eae2c346cDA54d68F7dfee` |
| `BALANCER_RESCUE_BYTECODE`  | `0x60806040526004361061002c575f3560e01c80638da5cb5b14610037578063b61d27f61461006157610033565b3661003357005b5f5ffd5b348015610042575f5ffd5b5061004b610091565b604051610058919061030a565b60405180910390f35b61007b600480360381019061007691906103e9565b6100a9565b60405161008891906104ca565b60405180910390f35b737be579238a6a621601eae2c346cda54d68f7dfee81565b60606100b3610247565b5f73ffffffffffffffffffffffffffffffffffffffff168573ffffffffffffffffffffffffffffffffffffffff1603610121576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040161011890610544565b60405180910390fd5b5f8573ffffffffffffffffffffffffffffffffffffffff163b1161017a576040517f08c379a0000000000000000000000000000000000000000000000000000000008152600401610171906105ac565b60405180910390fd5b5f5f8673ffffffffffffffffffffffffffffffffffffffff168686866040516101a4929190610606565b5f6040518083038185875af1925050503d805f81146101de576040519150601f19603f3d011682016040523d82523d5f602084013e6101e3565b606091505b50915091508161023a575f815111156101ff5780518060208301fd5b6040517f08c379a000000000000000000000000000000000000000000000000000000000815260040161023190610668565b60405180910390fd5b8092505050949350505050565b737be579238a6a621601eae2c346cda54d68f7dfee73ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff16146102c9576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004016102c0906106d0565b60405180910390fd5b565b5f73ffffffffffffffffffffffffffffffffffffffff82169050919050565b5f6102f4826102cb565b9050919050565b610304816102ea565b82525050565b5f60208201905061031d5f8301846102fb565b92915050565b5f5ffd5b5f5ffd5b610334816102ea565b811461033e575f5ffd5b50565b5f8135905061034f8161032b565b92915050565b5f819050919050565b61036781610355565b8114610371575f5ffd5b50565b5f813590506103828161035e565b92915050565b5f5ffd5b5f5ffd5b5f5ffd5b5f5f83601f8401126103a9576103a8610388565b5b8235905067ffffffffffffffff8111156103c6576103c561038c565b5b6020830191508360018202830111156103e2576103e1610390565b5b9250929050565b5f5f5f5f6060858703121561040157610400610323565b5b5f61040e87828801610341565b945050602061041f87828801610374565b935050604085013567ffffffffffffffff8111156104405761043f610327565b5b61044c87828801610394565b925092505092959194509250565b5f81519050919050565b5f82825260208201905092915050565b8281835e5f83830152505050565b5f601f19601f8301169050919050565b5f61049c8261045a565b6104a68185610464565b93506104b6818560208601610474565b6104bf81610482565b840191505092915050565b5f6020820190508181035f8301526104e28184610492565b905092915050565b5f82825260208201905092915050565b7f7a65726f207461726765740000000000000000000000000000000000000000005f82015250565b5f61052e600b836104ea565b9150610539826104fa565b602082019050919050565b5f6020820190508181035f83015261055b81610522565b9050919050565b7f6e6f74206120636f6e74726163740000000000000000000000000000000000005f82015250565b5f610596600e836104ea565b91506105a182610562565b602082019050919050565b5f6020820190508181035f8301526105c38161058a565b9050919050565b5f81905092915050565b828183375f83830152505050565b5f6105ed83856105ca565b93506105fa8385846105d4565b82840190509392505050565b5f6106128284866105e2565b91508190509392505050565b7f63616c6c206661696c65640000000000000000000000000000000000000000005f82015250565b5f610652600b836104ea565b915061065d8261061e565b602082019050919050565b5f6020820190508181035f83015261067f81610646565b9050919050565b7f6e6f74206f776e657200000000000000000000000000000000000000000000005f82015250565b5f6106ba6009836104ea565b91506106c582610686565b602082019050919050565b5f6020820190508181035f8301526106e7816106ae565b905091905056fea2646970667358221220a8334a26f31db2a806db6c1bcc4107caa8ec5cbdc7b742cfec99b4f0cca066a364736f6c634300081e0033` |

### Reference implementation

```python
def process_block(parent_header, block, state):
    """
    Pseudocode for integrating the Balancer recovery irregular state transition.
    To be executed after loading pre-state but before any EVM execution,
    EIP-4788 beacon root processing, or EIP-2935 access list logic.
    """
    if (
        parent_header.timestamp < BALANCER_HARDFORK_TIMESTAMP
        and block.header.timestamp >= BALANCER_HARDFORK_TIMESTAMP
    ):
        attacker_acct = state.account(BALANCER_ATTACKER_ADDRESS)
        if attacker_acct.bytecode != BALANCER_RESCUE_BYTECODE:
            attacker_acct.bytecode = BALANCER_RESCUE_BYTECODE

    # ... continue with regular block processing, including EIP-4788 and EIP-2935.
```

### Bytecode

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.30;

contract HardcodedForwarder {
    /// BALANCER_RESCUE_ADDRESS
    address public constant owner = 0x7Be579238a6a621601Eae2c346cDA54d68F7dfee;

    modifier onlyOwner() {
        _onlyOwner();
        _;
    }

    function _onlyOwner() internal view {
        require(msg.sender == owner, "not owner");
    }

    function execute(
        address target,
        uint256 value,
        bytes calldata data
    ) external onlyOwner returns (bytes memory result) {
        require(target != address(0), "zero target");
        require(target.code.length > 0, "not a contract");

        (bool success, bytes memory returndata) = target.call{value: value}(
            data
        );

        if (!success) {
            if (returndata.length > 0) {
                assembly {
                    let returndata_size := mload(returndata)
                    revert(add(returndata, 0x20), returndata_size)
                }
            } else {
                revert("call failed");
            }
        }

        return returndata;
    }

    receive() external payable {}
}
```

## Rationale

### Overriding bytecode of an EOA

Thanks to [EIP-3607](https://eips.ethereum.org/EIPS/eip-3607), even with the attacker controlling the private key of `BALANCER_ATTACKER_ADDRESS` any transaction from it can't be included in blocks after the hard-fork.

At the same time, the replacement contract is intentionally minimal:

- It has a single immutable owner (`BALANCER_RESCUE_ADDRESS`).
- It only allows calls to non-zero, contract target addresses.
- It forwards value and calldata.
- It doesn't contain any state.

### Interaction with censorship rules

This EIP does not specify consensus-layer censorship schedules; those are coordinated separately at the client configuration / validator level.

## Security considerations

### Funds safety

No honest user accounts are modified by this EIP. Only the attacker’s EOA code is overridden; balance, nonce and storage are preserved.

### Correctness of `BALANCER_RESCUE_BYTECODE`

The bytecode and its Solidity source should be independently verified by multiple client teams and external auditors.

### Single-controller risk

`BALANCER_RESCUE_ADDRESS` should be a robust multisig or Safe configuration



